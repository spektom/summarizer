import heapq

from datetime import timedelta, datetime
from urllib.parse import urlparse

from . import get_nlp
from .app import app, db
from .model import RecentArticle
from .nlp import drop_stop_words


class JaccardSimilarity(object):
    def __init__(self, lifetime=timedelta(hours=12)):
        self.lifetime = lifetime
        self.recent = []

        app.logger.info('Loading recent documents')
        for r in RecentArticle.query.filter(
                RecentArticle.create_time > datetime.utcnow() - lifetime).all():
            heapq.heappush(
                self.recent,
                (r.create_time, r.id, self.title_to_wordset_(r.title), r.site))

    def title_to_wordset_(self, title):
        nlp = get_nlp()
        return set([
            t.lemma_ for t in drop_stop_words(nlp(title)) if t.pos_ == 'VERB' or (
                t.pos_ == 'PROPN' and t.ent_type_ in ['ORG', 'PERSON', 'PRODUCT'])
        ])

    def get_similarity_score_(self, s1, s2):
        i = s1.intersection(s2)
        return len(i) / (len(s1) + len(s2) - len(i))

    def add_get_score(self, id, title, uri, create_time):
        words_set = self.title_to_wordset_(title)
        site = urlparse(uri).hostname

        scores = [
            0 if site == r[3] else self.get_similarity_score_(r[2], words_set)
            for r in self.recent if r[1] != id
        ]

        if RecentArticle.query.get(id) is None:
            db.session.add(
                RecentArticle(id=id, create_time=create_time, title=title, site=site))
            db.session.commit()

            heapq.heappush(self.recent, (create_time, id, words_set, site))
            while len(self.recent) > 0 \
                    and self.recent[0][0] <= datetime.utcnow() - self.lifetime:
                heapq.heappop(self.recent)

        return scores


def create_similar_articles_scorer(lifetime=timedelta(hours=12)):
    jaccard = JaccardSimilarity()
    return lambda id, title, uri, create_time: jaccard.add_get_score(
        id, title, uri, create_time)
