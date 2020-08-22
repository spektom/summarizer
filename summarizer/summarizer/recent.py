import heapq

from datetime import timedelta, datetime
from . import get_nlp
from .app import app, db
from .model import RecentTitle
from .nlp import drop_stop_words


def create_similar_titles_scorer(lifetime=timedelta(hours=12)):
    nlp = get_nlp()
    recent_titles = [(r.create_time, r.id, nlp(r.title))
                     for r in RecentTitle.query.filter(
                         RecentTitle.create_time > datetime.utcnow() - lifetime).all()]
    heapq.heapify(recent_titles)

    def score_title(id, title, create_time):
        title_doc = nlp(' '.join([t.lemma_ for t in drop_stop_words(nlp(title))]))
        scores = [title_doc.similarity(r[2]) for r in recent_titles if r[1] != id]
        if RecentTitle.query.get(id) is None:
            db.session.add(
                RecentTitle(id=id,
                            create_time=create_time,
                            title=' '.join([t.lemma_ for t in title_doc])))
            db.session.commit()

            heapq.heappush(recent_titles, (create_time, id, title_doc))
            while recent_titles[0][0] <= datetime.utcnow() - lifetime:
                heapq.heappop(recent_titles)
        return scores

    return score_title
