import joblib
import logging
import re
import statistics
import math
import multiprocessing as mp

from sklearn.feature_extraction.text import TfidfVectorizer
from .html import html_to_clean_text
from . import get_nlp


def run_in_parallel(func, objs):
    with mp.Pool() as pool:
        return pool.map(func, objs)


SUBJ_DEP = set(['agent', 'csubj', 'csubjpass', 'expl', 'nsubj', 'nsubjpass'])
AUX_DEP = set(['aux', 'auxpass'])


def is_relevant_sentence(sentence):
    """Decides whether such a sentence is wanted in a summary"""
    # Sentence must have a subject with a verb
    if next(
        (subj for verb in sentence for subj in verb.lefts
         if verb.pos_ == 'VERB' and verb.dep_ not in AUX_DEP and subj.dep_ in SUBJ_DEP),
            None) is None:
        return False

    # Sentences must end with a dot
    if not sentence.text.strip().endswith('.'):
        return False

    return True


def clean_sentence(sentence):
    """Remove irrelevant elements from a sentence prior to building a summary"""
    sentence_pos = [t.pos_ for t in sentence]
    sentence_lemmas = [t.lemma_ for t in sentence]

    # Drop any punctuation from the beginning (except for quotes)
    start = 0
    for tok in sentence:
        if tok.pos_ != 'PUNCT' or tok.is_quote:
            break
        start += 1
    sentence = sentence[start:]

    # Remove prefixes by lemmas
    for drop_prefix in [['on', 'top', 'of', 'that', ','], ['that', 'say', ',']]:
        if sentence_lemmas[:len(drop_prefix)] == drop_prefix:
            sentence = sentence[len(drop_prefix):]
            break

    # Remove prefixes by POS tags
    for drop_prefix in [['ADV', 'PUNCT'], ['ADV', 'ADV', 'PUNCT'], ['INTJ', 'PUNCT'],
                        ['CCONJ', 'PUNCT'], ['CCONJ']]:
        if sentence_pos[:len(drop_prefix)] == drop_prefix:
            sentence = sentence[len(drop_prefix):]
            break

    # Remove endings that start with specific lemmas
    for drop_suffix in [[',', 'say'], [',', '-PRON-', 'say'], [',', '-PRON-', 'tell']]:
        for i in range(len(sentence_lemmas)):
            if sentence_lemmas[i] == drop_suffix[0] and sentence_lemmas[
                    i:i + len(drop_suffix)] == drop_suffix:
                sentence = sentence[:i]
                break
        else:
            continue
        break

    return sentence


def drop_irrelevant_sentences(sentences):
    return [clean_sentence(sent) for sent in sentences if is_relevant_sentence(sent)]


def drop_stop_words(doc):
    return [
        token for token in doc
        if not token.is_stop and re.search(r'^[A-Za-z]{2,}', token.lemma_)
    ]


def clean_result(sentence):
    """Clean the result as it will be shown in a summary"""
    text = sentence.text.strip()

    # Capitalize
    if not text[0].isupper():
        text = text[0].upper() + text[1:]

    text = re.sub(r'\s+([,\!\.])', r'\1', text)
    text = re.sub(r'\s\s+', ' ', text)

    if not text.endswith('.'):
        text += '.'

    return text


def is_news_title(title):
    nlp = get_nlp()
    doc = nlp(title)
    lemmas = [t.lemma_ for t in doc]

    if len(doc) < 2:
        return False

    if lemmas[0] == 'the' and doc[1].text == 'best':
        return False

    if lemmas[0] == 'save' and doc[1].pos_ == 'SYM':
        return False

    for i in range(len(doc) - 1):
        if lemmas[i:i + 2] == ['how', 'to'] and (i == 0 or doc[i - 1].pos_ == 'PUNCT'):
            # Promotional "tutorials"
            return False

        if doc[i].pos_ == 'NUM' and lemmas[i + 1:i + 3] == ['%', 'discount']:
            return False

        if doc[i].pos_ == 'SYM' and doc[i + 1].pos_ == 'NUM' and 'deal' in lemmas:
            return False

    return True


def train_and_save(htmls, model_file='dtm.model'):
    nlp = get_nlp()
    logging.info('Started procesing %d documents', len(htmls))

    logging.info('Converting HTML to text')
    texts = run_in_parallel(html_to_clean_text, htmls)

    logging.info('Analyzing documents')
    docs = nlp.pipe(texts, batch_size=100, n_process=mp.cpu_count())

    logging.info('Removing stop words')
    docs_sents = run_in_parallel(lambda doc: drop_irrelevant_sentences(doc.sents), docs)
    docs_for_train = run_in_parallel(
        lambda doc_sents: ' '.join(
            [token.lemma_ for sent in doc_sents for token in drop_stop_words(sent)]),
        docs_sents)

    logging.info('Started building document-term matrix')
    tfidf = TfidfVectorizer()
    tfidf.fit(docs_for_train)
    logging.info('Finished building document-term matrix')

    joblib.dump(tfidf, model_file)
    logging.info(f'Saved model to file {model_file}')


def summarize(tfidf, feature_indices, title, html, top_n):
    nlp = get_nlp()
    doc = nlp(html_to_clean_text(html))
    sentences = drop_irrelevant_sentences(doc.sents)
    doc_for_train = ' '.join(
        [token.lemma_ for sent in sentences for token in drop_stop_words(sent)])

    logging.debug('Building document terms frequency')
    doc_freq = tfidf.transform([doc_for_train]).todense().tolist()[0]

    logging.debug('Scoring sentences')

    # Score sentences based on word frequencies (only nouns are taken into account)
    sentences_freqs = [[
        doc_freq[feature_indices[t.lemma_]] for t in sent
        if t.pos_ == 'NOUN' and t.lemma_ in feature_indices
    ] for sent in sentences]
    doc_freq_sum = sum(doc_freq)
    frequency_scores = [
        sum(sentence_freq) / doc_freq_sum for sentence_freq in sentences_freqs
    ]

    # Increment scores of sentences similar to title
    title_tokens = nlp(' '.join([t.lemma_ for t in drop_stop_words(nlp(title))]))
    sentences_tokens = [
        nlp(' '.join([t.lemma_ for t in drop_stop_words(sent)])) for sent in sentences
    ]
    similarity_scores = [
        0.0 if len(tokens) == 0 else tokens.similarity(title_tokens)
        for tokens in sentences_tokens
    ]

    # Length-based score
    length_scores = [
        0.1 / (1 + math.fabs(20.0 - len(sentence))) for sentence in sentences
    ]

    # Calc total score, and sort by it
    total_scores = [(index, frequency_scores[index] * 0.5 +
                     similarity_scores[index] * 0.4 + length_scores[index] * 0.1)
                    for index in range(len(sentences))]
    total_scores = sorted(total_scores, key=lambda x: x[1] * -1)

    # Choose top N from original sentences
    result = []
    seen = set()
    if len(total_scores) > 0:
        # Set threshold to average score
        threshold = sum([r[1] for r in total_scores]) / len(total_scores)
        for index, score in total_scores:
            if len(result) >= top_n:  # or score < threshold:
                break
            sentence = clean_result(sentences[index])
            if not sentence in seen:
                result.append((index, sentence))
                seen.add(sentence)
    result = [s for _, s in sorted(result, key=lambda x: x[0])]
    return result, doc_for_train


def create_summarizer(model_file='dtm.model'):
    get_nlp()
    logging.info(f'Loading model from file {model_file}')
    tfidf = joblib.load(model_file)

    logging.info(f'Initializing summarizer')
    feature_names = tfidf.get_feature_names()
    feature_indices = {n: i for i, n in enumerate(feature_names)}

    return lambda title, html, top_n: summarize(tfidf, feature_indices, title, html,
                                                top_n)
