#!/usr/bin/env python3

import joblib
import logging
import nltk
import re

from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from nltk.stem.wordnet import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer

nltk.data.path.append('.data')


def is_word(token):
    return re.search(r'[a-zA-Z]', token)


stop_words_ = set([word for word in stopwords.words('english') if is_word(word)])


def is_stop_word(word):
    return is_word(word) and word not in stop_words_


def drop_stop_words(words):
    for word in words:
        if not is_stop_word(word):
            yield word


def tokenize(text):
    for sent in nltk.sent_tokenize(text):
        for word in nltk.word_tokenize(sent):
            if not is_stop_word(word):
                yield word


stemmer_ = SnowballStemmer('english')
lemmatizer_ = WordNetLemmatizer()


def stem_or_lemmatize(tokens):
    for token in tokens:
        s = stemmer_.stem(token)
        if s == token:
            s = lemmatizer_.lemmatize(token)
        yield s


def tokenize_and_stem(text):
    return stem_or_lemmatize(tokenize(text))


stemmed_stop_words_ = tokenize_and_stem(' '.join(stop_words_))


def build_document_term_matrix(docs, output_file):
    tfidf = TfidfVectorizer(tokenizer=tokenize_and_stem,
                            stop_words=stemmed_stop_words_,
                            decode_error='ignore')
    logging.info('Started building document-term matrix for %d documents', len(docs))

    dtm = tfidf.fit_transform(docs)
    logging.info('Finished building document-term matrix')

    logging.info(f'Saving model to file {output_file}')
    joblib.dump(dtm, output_file)
