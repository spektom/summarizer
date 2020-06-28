#!/usr/bin/env python3

import logging
import sqlite3

from summarizer import train_and_save


def read_articles():
    db = sqlite3.connect('../manager/manager.db')
    c = db.cursor()
    logging.info('Loading documents from DB')
    articles = [r[0] for r in c.execute("SELECT html FROM article WHERE status='D'")]
    db.close()
    return articles


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)s %(module)s: %(message)s')

    train_and_save(read_articles())