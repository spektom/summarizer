import heapq

from datetime import timedelta, datetime
from lru import LRU

from .app import app, db
from .model import RecentArticle


class TFIDFScorer(object):
    def __init__(self, lifetime=timedelta(hours=12)):
        self.lifetime = lifetime
        self.words = LRU(10000)
        self.recent = []
        app.logger.info('Loading recent documents')
        for r in RecentArticle.query.all():
            word_vec = self.get_word_vec_(r.text)
            heapq.heappush(self.recent, (r.create_time, r.id, word_vec))

    def get_word_vec_(self, text):
        word_vec = set()
        for word in text.split():
            if word in self.words:
                idx = self.words[word]
            else:
                self.words[word] = idx = len(self.words)
            word_vec.add(idx)
        return word_vec

    def get_similarity_score_(self, vec1, vec2):
        same_count = 0
        for n in vec1:
            if n in vec2:
                same_count += 1
        min_len = min(len(vec1), len(vec2))
        return same_count / min_len if min_len > 0 else 0

    def add_get_score(self, id, text, create_time):
        word_vec = self.get_word_vec_(text)

        scores = [
            self.get_similarity_score_(r[2], word_vec) for r in self.recent
            if r[1] != id
        ]

        if RecentArticle.query.get(id) is None:
            db.session.add(RecentArticle(id=id, create_time=create_time, text=text))
            db.session.commit()

            heapq.heappush(self.recent, (create_time, id, text))
            while len(self.recent) > 0 \
                    and self.recent[0][0] <= datetime.utcnow() - self.lifetime:
                heapq.heappop(self.recent)

        return scores


def create_similar_articles_scorer(lifetime=timedelta(hours=12)):
    tfidf_scorer = TFIDFScorer()
    return lambda id, text, create_time: tfidf_scorer.add_get_score(
        id, text, create_time)
