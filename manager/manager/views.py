from flask import render_template
from .app import app
from .model import Article


@app.route('/article/<id>', methods=['GET'])
def read_article(id):
    article = Article.query.get_or_404(id)
    return render_template('reader.html', article=article)
