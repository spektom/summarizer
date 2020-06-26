#!/usr/bin/env python3

import argparse
import bs4
import logging
import sqlite3

from summarizer import train_and_save, create_summarizer


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
    parser.add_argument('command',
                        help='Command to run',
                        choices=['train', 'summarize', 'app'])
    parser.add_argument('-i',
                        '--input_file',
                        dest='input_file',
                        help='Input file containing the document to summarize')
    return parser.parse_args()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)s %(module)s: %(message)s')

    options = parse_args()

    if options.command == 'train':
        train_and_save(read_articles())

    if options.command == 'summarize':
        summarize = create_summarizer()
        with open(options.input_file, 'r') as f:
            l = f.readlines()
            print('\n\n'.join(summarize('\n'.join(l[1:]), l[0], 4)))

    if options.command == 'app':
        from summarizer.api import app
        app.run(port=6000)
