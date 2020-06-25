#!/usr/bin/env python3

import argparse
import bs4
import logging
import sqlite3

from summarizer.lib import build_document_term_matrix


def read_articles():
    db = sqlite3.connect('../manager/manager.db')
    c = db.cursor()
    logging.info('Loading documents from DB')
    articles = [r[0] for r in c.execute("SELECT html FROM article WHERE status='D'")]
    db.close()
    logging.info('Extracting text from HTML')
    return [bs4.BeautifulSoup(a, 'lxml').get_text() for a in articles]


def parse_args():
    parser = argparse.ArgumentParser(usage='usage: %(prog)s [options]')
    parser.add_argument('command', help='Command to run', choices=['dtm'])
    parser.add_argument('-o',
                        '--output_file',
                        dest='output_file',
                        default='dtm.model',
                        help='Model output file')
    return parser.parse_args()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)s %(module)s: %(message)s')
    options = parse_args()
    if options.command == 'dtm':
        build_document_term_matrix(read_articles(), options.output_file)
