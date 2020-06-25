import joblib
import logging
import nltk
import re

from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from nltk.stem.wordnet import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer

for p in ['stopwords', 'punkt', 'wordnet', 'averaged_perceptron_tagger']:
    nltk.download(p, download_dir='.data', quiet=True)

nltk.data.path.append('.data')

stopwords_ = set(stopwords.words('english'))
stemmer_ = SnowballStemmer('english')
lemmatizer_ = WordNetLemmatizer()
nouns_ = set(['NN', 'NNS', 'NNP', 'NNPS'])
pronouns_ = set(['PRP', 'PRP$'])


def retain_nouns(words):
    return [word for word, pos in nltk.pos_tag(words) if pos in nouns_]


def drop_stopwords(words):
    return [word for word in words if word not in stopwords_]


def drop_nonwords(words):
    return [word for word in words if re.search(r'[A-Za-z]{3,}', word)]


def stem_or_lemmatize_token(token):
    s = stemmer_.stem(token)
    if s == token:
        s = lemmatizer_.lemmatize(token)
    return s


def stem_or_lemmatize(tokens):
    return [stem_or_lemmatize_token(t) for t in tokens]


def drop_non_sentences(text):
    lines = [line.strip() for line in text.split('\n')]
    lines = [
        line for line in lines
        if len(line) > 0 and '.' in line and len(re.findall(r'\s+', line)) > 3
    ]
    text = ' '.join(lines)
    return text


def drop_pronouns_sentences(sentences):
    return [
        sentence for sentence in sentences if nltk.pos_tag(
            [drop_nonwords(nltk.word_tokenize(sentence))[0]])[0][1] not in pronouns_
    ]


def clean_for_training(doc=None, sentences=None):
    sentences = sentences or nltk.sent_tokenize(doc)
    return ' '.join([
        word for sentence in sentences for word in stem_or_lemmatize(
            drop_stopwords(drop_nonwords(nltk.word_tokenize(sentence))))
    ])


def train_and_save(docs, model_file='dtm.model'):
    logging.info('Started procesing %d documents', len(docs))
    docs = [clean_for_training(doc=drop_non_sentences(doc)) for doc in docs]

    tfidf = TfidfVectorizer()
    logging.info('Started building document-term matrix')

    tfidf.fit(docs)
    logging.info('Finished building document-term matrix')

    joblib.dump(tfidf, model_file)
    logging.info(f'Saved model to file {model_file}')


def summarize(tfidf, feature_indices, doc, title, top_n=5):
    doc = drop_non_sentences(doc)

    logging.info('Building document terms frequency')

    # Save original sentences for constructing a summary later
    sentences = drop_pronouns_sentences(nltk.sent_tokenize(doc))

    doc_freq = tfidf.transform([clean_for_training(sentences=sentences)
                                ]).todense().tolist()[0]

    logging.info('Ranking sentences')

    tokenized_sentences = [
        nltk.word_tokenize(sentence.lower()) for sentence in sentences
    ]

    # Word frequencies in sentences (only nouns are taken into account)
    sentences_nouns = [
        stem_or_lemmatize(retain_nouns(sentence)) for sentence in tokenized_sentences
    ]
    sentences_freqs = [[
        doc_freq[feature_indices[word]] for word in words if word in feature_indices
    ] for words in sentences_nouns]

    # Sentences frequences
    doc_freq_sum = sum(doc_freq)
    sentences_freqs = [
        sum(sentence_freq) / doc_freq_sum for sentence_freq in sentences_freqs
    ]

    # Sentence indices and their ranks
    ranked_sentences_indices = enumerate(sentences_freqs)
    ranked_sentences_num = len(sentences_freqs)

    # Add similarity to title to sentence scores
    title_tokens = set(
        [t.lower() for t in drop_stopwords(drop_nonwords(nltk.word_tokenize(title)))])
    sentences_tokens = [
        drop_stopwords(drop_nonwords(words)) for words in tokenized_sentences
    ]
    similarity_scores = [
        len([t for t in tokens if t in title_tokens]) * 0.1 / len(title_tokens)
        for tokens in sentences_tokens
    ]
    ranked_sentences_indices = [(index, rank + similarity_scores[index])
                                for index, rank in ranked_sentences_indices]

    # Apply position based weight
    ranked_sentences_indices = [(index, rank * (index / ranked_sentences_num))
                                for index, rank in ranked_sentences_indices]

    # Sort by rank
    ranked_sentences_indices = sorted(ranked_sentences_indices,
                                      key=lambda index_rank: index_rank[1] * -1)

    # Choose top N from original sentences
    result = [title]
    for index, _ in ranked_sentences_indices:
        sentence = sentences[index]
        if sentence not in result:
            result.append(sentence)
        if len(result) >= top_n:
            break
    return result


def create_summarizer(model_file='dtm.model'):
    logging.info(f'Loading model from file {model_file}')
    tfidf = joblib.load(model_file)

    feature_names = tfidf.get_feature_names()
    feature_indices = {n: i for i, n in enumerate(feature_names)}

    logging.info(f'Initializing summarizer')
    return lambda doc, title: summarize(tfidf, feature_indices, doc, title)
