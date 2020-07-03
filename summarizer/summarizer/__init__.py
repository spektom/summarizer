import bs4
import joblib
import logging
import re
import spacy
import statistics
import multiprocessing as mp

from sklearn.feature_extraction.text import TfidfVectorizer


def init_nlp():
    global nlp
    model = 'en_core_web_md'
    logging.info(f'Loading NLP model: {model}')
    nlp = spacy.load(model)


def html_to_text(html):
    soup = bs4.BeautifulSoup(html, 'lxml')
    for e in soup.select('#engadget-article-footer'):
        e.decompose()
    return soup.get_text(' ')


def clean_text(text):
    """Preliminary text cleaning"""
    lines = text.split('\n')

    # Drop non-sentences (ones that don't have a dot in them), while relying on Reader View
    # plug-in HTML structure:
    lines = [line for line in lines if len(line) > 0 and '.' in line]

    return ' '.join(lines)


def run_in_parallel(func, objs):
    with mp.Pool(mp.cpu_count()) as pool:
        return pool.map(func, objs)


def retain_sentences_with_verbs(sentences):
    return [sent for sent in sentences if \
        next((s for s in sent if s.pos_ == 'VERB'), None) is not None \
        and len(sent) >= 5
    ]


def drop_stop_words(doc):
    return [
        token for token in doc
        if not token.is_stop and re.search(r'^[A-Za-z]{2,}', token.lemma_)
    ]


def is_relevant_sentence(sentence):
    """Decides whether such a sentence is wanted in a summary"""
    # Sentences must contain at least one verb
    if next((t for t in sentence if t.pos_ == 'VERB'), None) is None:
        return False

    # Sentences must end with a dot
    if not sentence.text.strip().endswith('.'):
        return False

    return True


def clean_sentence(sentence):
    """Remove irrelevant elements from a sentence prior to building a summary"""

    # Remove adverbs from the beginning ("Also, ", "Moreover, ", etc.)
    sentence_pos = [t.pos_ for t in sentence]
    for drop_prefix in [['ADV', 'PUNCT'], ['ADV', 'ADV', 'PUNCT'], ['INTJ', 'PUNCT']]:
        if sentence_pos[:len(drop_prefix)] == drop_prefix:
            sentence = sentence[len(drop_prefix):]
            break

    return sentence


def clean_result(sentence):
    """Clean the result as it will be shown in a summary"""
    text = sentence.text.strip()

    # Capitalize
    if not text[0].isupper():
        text = text[0].upper() + text[1:]

    text = re.sub(r'\s+\.$', '.', text)
    text = re.sub(r'  +', ' ', text)

    return text


def train_and_save(htmls, model_file='dtm.model'):
    init_nlp()

    logging.info('Started procesing %d documents', len(htmls))

    logging.info('Converting HTML to text')
    texts = run_in_parallel(html_to_text, htmls)

    logging.info('Cleaning up texts')
    texts = run_in_parallel(clean_text, texts)

    logging.info('Removing stop words')
    docs = nlp.pipe(texts, batch_size=100, n_process=mp.cpu_count())
    docs_sents = [retain_sentences_with_verbs(doc.sents) for doc in docs]
    docs_for_train = [
        ' '.join(
            [token.lemma_ for sent in doc_sents for token in drop_stop_words(sent)])
        for doc_sents in docs_sents
    ]

    tfidf = TfidfVectorizer()
    logging.info('Started building document-term matrix')

    tfidf.fit(docs_for_train)
    logging.info('Finished building document-term matrix')

    joblib.dump(tfidf, model_file)
    logging.info(f'Saved model to file {model_file}')


def summarize(tfidf, feature_indices, title, html, top_n):
    text = html_to_text(html)
    text = clean_text(text)
    doc = nlp(text)
    sentences = retain_sentences_with_verbs(doc.sents)
    doc_for_train = ' '.join(
        [token.lemma_ for sent in sentences for token in drop_stop_words(sent)])

    logging.debug('Building document terms frequency')

    doc_freq = tfidf.transform([doc_for_train]).todense().tolist()[0]

    logging.debug('Ranking sentences')

    # Drop irrelevant sentences
    sentences = [
        clean_sentence(sent) for sent in sentences if is_relevant_sentence(sent)
    ]

    # Word frequencies in sentences (only nouns are taken into account)
    sentences_freqs = [[
        doc_freq[feature_indices[t.lemma_]] for t in sent
        if t.pos_ == 'NOUN' and t.lemma_ in feature_indices
    ] for sent in sentences]

    # Sentences frequences
    doc_freq_sum = sum(doc_freq)
    sentences_freqs = [
        sum(sentence_freq) / doc_freq_sum for sentence_freq in sentences_freqs
    ]

    # Sentence indices and their ranks
    sentences_ranks = enumerate(sentences_freqs)
    ranked_sentences_num = len(sentences_freqs)

    # Increment scores of sentences similar to title
    title_tokens = nlp(' '.join([t.lemma_ for t in drop_stop_words(nlp(title))]))
    sentences_tokens = [
        nlp(' '.join([t.lemma_ for t in drop_stop_words(sent)])) for sent in sentences
    ]
    similarity_scores = [tokens.similarity(title_tokens) for tokens in sentences_tokens]
    sentences_ranks = [(index, rank + similarity_scores[index])
                       for index, rank in sentences_ranks]

    # Sort by rank
    sentences_ranks = sorted(sentences_ranks, key=lambda x: x[1] * -1)

    # Choose top N from original sentences
    result = []
    if len(sentences_ranks) > 0:
        # Rank threshold
        threshold = sum([r[1] for r in sentences_ranks]) / len(sentences_ranks)
        for index, rank in sentences_ranks:
            if len(result) >= top_n or rank < threshold:
                break
            sentence = clean_result(sentences[index])
            if sentence not in result:
                result.append(sentence)
    return result


def create_summarizer(model_file='dtm.model'):
    logging.info(f'Loading model from file {model_file}')
    tfidf = joblib.load(model_file)

    feature_names = tfidf.get_feature_names()
    feature_indices = {n: i for i, n in enumerate(feature_names)}

    logging.info(f'Initializing summarizer')
    init_nlp()

    return lambda title, html, top_n: summarize(tfidf, feature_indices, title, html,
                                                top_n)
