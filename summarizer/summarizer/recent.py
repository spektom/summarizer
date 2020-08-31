import heapq

from datetime import timedelta, datetime

from . import get_nlp
from .app import app, db
from .model import RecentArticle
from .nlp import drop_stop_words


class JaccardSimilarity(object):
    def __init__(self, lifetime=timedelta(hours=12)):
        self.lifetime = lifetime
        self.recent = []

        app.logger.info('Loading recent documents')
        nlp = get_nlp()
        for r in RecentArticle.query.filter(
                RecentArticle.create_time > datetime.utcnow() - lifetime).all():
            heapq.heappush(self.recent,
                           (r.create_time, r.id,
                            set([t.lemma_ for t in drop_stop_words(nlp(r.title))])))

    def get_similarity_score_(self, s1, s2):
        i = s1.intersection(s2)
        return len(i) / (len(s1) + len(s2) - len(i))

    def add_get_score(self, id, title, create_time):
        nlp = get_nlp()
        words_set = set([t.lemma_ for t in drop_stop_words(nlp(title))])

        scores = [
            self.get_similarity_score_(r[2], words_set) for r in self.recent
            if r[1] != id
        ]

        if RecentArticle.query.get(id) is None:
            db.session.add(RecentArticle(id=id, create_time=create_time, title=title))
            db.session.commit()

            heapq.heappush(self.recent, (create_time, id, words_set))
            while len(self.recent) > 0 \
                    and self.recent[0][0] <= datetime.utcnow() - self.lifetime:
                heapq.heappop(self.recent)

        return scores


def create_similar_articles_scorer(lifetime=timedelta(hours=12)):
    jaccard = JaccardSimilarity()
    return lambda id, title, create_time: jaccard.add_get_score(id, title, create_time)
