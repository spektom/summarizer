import heapq

from datetime import timedelta, datetime
from . import get_nlp
from .app import app, db
from .model import RecentArticle
from .nlp import drop_stop_words


def create_similar_articles_scorer(lifetime=timedelta(hours=12)):
    nlp = get_nlp()
    recent_articles = [
        (r.create_time, r.id, nlp(r.article)) for r in RecentArticle.query.filter(
            RecentArticle.create_time > datetime.utcnow() - lifetime).all()
    ]
    heapq.heapify(recent_articles)

    def score_article(id, text, create_time):
        doc = nlp(' '.join([t.lemma_ for t in drop_stop_words(nlp(text))]))
        scores = [doc.similarity(r[2]) for r in recent_articles if r[1] != id]
        if RecentArticle.query.get(id) is None:
            db.session.add(
                RecentArticle(id=id,
                              create_time=create_time,
                              text=' '.join([t.lemma_ for t in doc])))
            db.session.commit()

            heapq.heappush(recent_articles, (create_time, id, doc))
            while len(recent_articles) > 0 \
                    and recent_articles[0][0] <= datetime.utcnow() - lifetime:
                heapq.heappop(recent_articles)
        return scores

    return score_article
