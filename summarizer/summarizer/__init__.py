import logging
import spacy

nlp_ = None

def get_nlp():
    global nlp_
    if nlp_ is None:
        model = 'en_core_web_lg'
        logging.info(f'Loading NLP model: {model}')
        nlp_ = spacy.load(model)
    return nlp_
