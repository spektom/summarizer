#!/usr/bin/env python3

import logging
import sqlite3
import sys

from summarizer.nlp import create_summarizer


def read_article(id):
    db = sqlite3.connect('../manager/manager.db')
    c = db.cursor()
    title, html = c.execute("SELECT title,html FROM article WHERE id=?",
                            (id, )).fetchone()
    db.close()
    return title, html


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)s %(module)s: %(message)s')

    title, html = read_article(int(sys.argv[1]))

    summarize = create_summarizer()
    print(f'{title}\n\n')
    print('\n\n'.join(summarize(title, html, 4)))
