import bs4
import joblib
import logging
import re
import spacy

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
    # Trim lines
    lines = [line.strip() for line in text.split('\n')]

    # Drop non-sentences (ones that don't have a dot in them), while relying on readability
    # plug-in HTML structure:
    lines = [
        line for line in lines
        if len(line) > 0 and '.' in line and len(re.findall(r'\s+', line)) > 3
    ]

    return ' '.join(lines)


def clean_for_training(doc):
    if not isinstance(doc, spacy.tokens.doc.Doc):
        doc = nlp(doc)
    lemmas = [
        token.lemma_ for token in doc
        if not token.is_stop and re.search(r'[A-Za-z]{3,}', token.lemma_)
    ]
    return ' '.join(lemmas)


def is_relevant_sentence(sentence):
    """Decides whether such a sentence is wanted in a summary"""
    # Sentences shouldn't contain pronoun before comma
    for t in sentence:
        if t.lemma_ == ',':
            break
        if t.pos_ == 'PRON':
            return False

    # Sentences must contain at least one verb
    if len([t for t in sentence if t.pos_ == 'VERB']) == 0:
        return False

    # Sentences must end with a dot
    if sentence[-1].lemma_ != '.':
        return False

    return True


def clean_sentence(sentence):
    """Remove irrelevant elements from a sentence"""

    # Remove adverbs from the beginning ("Also, ", "Moreover, ", etc.)
    sentence_pos = [t.pos_ for t in sentence]
    for drop_prefix in [['ADV', 'PUNCT'], ['ADV', 'ADV', 'PUNCT']]:
        if sentence_pos[:len(drop_prefix)] == drop_prefix:
            sentence = sentence[len(drop_prefix):]
            break

    return sentence


def clean_result(text):
    text = text.strip()

    # Capitalize
    if not text[0].isupper():
        text = text[0].upper() + text[1:]

    text = re.sub(r'\s+\.$', '.', text)
    return text


def train_and_save(docs, model_file='dtm.model'):
    init_nlp()

    logging.info('Started procesing %d documents', len(docs))
    docs = [clean_for_training(clean_text(html_to_text(doc))) for doc in docs]

    tfidf = TfidfVectorizer()
    logging.info('Started building document-term matrix')

    tfidf.fit(docs)
    logging.info('Finished building document-term matrix')

    joblib.dump(tfidf, model_file)
    logging.info(f'Saved model to file {model_file}')


def summarize(tfidf, feature_indices, title, html, top_n):
    doc = nlp(clean_text(html_to_text(html)))

    logging.debug('Building document terms frequency')

    doc_freq = tfidf.transform([clean_for_training(doc)]).todense().tolist()[0]

    logging.debug('Ranking sentences')

    # Drop irrelevant sentences
    sentences = [
        clean_sentence(sent) for sent in doc.sents if is_relevant_sentence(sent)
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
    title_tokens = nlp(''.join([t.text_with_ws for t in nlp(title) if not t.is_stop]))
    sentences_tokens = [
        nlp(''.join([t.text_with_ws for t in sent if not t.is_stop]))
        for sent in sentences
    ]
    similarity_scores = [tokens.similarity(title_tokens) for tokens in sentences_tokens]
    sentences_ranks = [(index, rank + similarity_scores[index])
                       for index, rank in sentences_ranks]

    # Apply position based weight
    sentences_ranks = [(index, rank * (index / ranked_sentences_num))
                       for index, rank in sentences_ranks]

    # Sort by rank
    sentences_ranks = sorted(sentences_ranks, key=lambda index_rank: index_rank[1] * -1)

    result = []

    # Choose top N from original sentences
    if len(sentences_ranks) > 0:

        # Rank threshold
        threshold = sum([r[1] for r in sentences_ranks]) / len(sentences_ranks)
        for index, rank in sentences_ranks:
            if len(result) >= top_n or rank < threshold:
                break
            sentence = clean_result(sentences[index].text)
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
