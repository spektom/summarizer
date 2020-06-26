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


def drop_non_sentences(text):
    lines = [line.strip() for line in text.split('\n')]
    lines = [
        line for line in lines
        if len(line) > 0 and '.' in line and len(re.findall(r'\s+', line)) > 3
    ]
    text = ' '.join(lines)
    return text


def clean_for_training(doc):
    if not isinstance(doc, spacy.tokens.doc.Doc):
        doc = nlp(doc)
    lemmas = [
        token.lemma_ for token in doc
        if not token.is_stop and re.search(r'[A-Za-z]{3,}', token.lemma_)
    ]
    return ' '.join(lemmas)


def train_and_save(docs, model_file='dtm.model'):
    logging.info('Started procesing %d documents', len(docs))
    docs = [clean_for_training(drop_non_sentences(doc)) for doc in docs]

    tfidf = TfidfVectorizer()
    logging.info('Started building document-term matrix')

    tfidf.fit(docs)
    logging.info('Finished building document-term matrix')

    joblib.dump(tfidf, model_file)
    logging.info(f'Saved model to file {model_file}')


def summarize(tfidf, feature_indices, text, title, top_n=5):
    doc = nlp(drop_non_sentences(text))

    logging.info('Building document terms frequency')

    doc_freq = tfidf.transform([clean_for_training(doc)]).todense().tolist()[0]

    logging.info('Ranking sentences')

    # Drop sentences containing pronouns (he, she, etc.)
    sentences = [
        sent for sent in doc.sents if len([t for t in sent if t.pos_ == 'PRON']) == 0
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
    title_tokens = set([t.lemma_ for t in nlp(title) if not t.is_stop])
    sentences_tokens = [[t.lemma_ for t in sent if not t.is_stop] for sent in sentences]
    similarity_scores = [
        len([t for t in tokens if t in title_tokens]) * 0.1 / len(title_tokens)
        for tokens in sentences_tokens
    ]
    sentences_ranks = [(index, rank + similarity_scores[index])
                       for index, rank in sentences_ranks]

    # Apply position based weight
    sentences_ranks = [(index, rank * (index / ranked_sentences_num))
                       for index, rank in sentences_ranks]

    # Sort by rank
    sentences_ranks = sorted(sentences_ranks, key=lambda index_rank: index_rank[1] * -1)

    # Rank threshold
    threshold = sum([r[1] for r in sentences_ranks]) / len(sentences_ranks)

    # Choose top N from original sentences
    result = []
    for index, rank in sentences_ranks:
        if len(result) >= top_n or rank < threshold:
            break
        sentence = sentences[index]
        if sentence.text not in result:
            result.append(sentence.text)
    return result


def create_summarizer(model_file='dtm.model'):
    logging.info(f'Loading model from file {model_file}')
    tfidf = joblib.load(model_file)

    feature_names = tfidf.get_feature_names()
    feature_indices = {n: i for i, n in enumerate(feature_names)}

    logging.info(f'Initializing summarizer')
    init_nlp()

    return lambda text, title: summarize(tfidf, feature_indices, text, title)
