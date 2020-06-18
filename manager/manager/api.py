from flask import request, jsonify
from .app import app, db
from .model import Task


@app.route('/tasks/next', methods=['GET'])
def tasks_next():
    task = Task.query.filter(Task.status == 'N').order_by(
        Task.create_time).first()
    if task is not None:
        task.status = 'Q'
        db.session.commit()
        return jsonify(uri=task.uri)
    return '', 204


@app.route('/tasks/add', methods=['POST'])
def tasks_add():
    task = request.json
    db.session.add(Task(uri=task['uri'], status='N'))
    db.session.commit()
    return '', 201

@app.route('/tasks/update', methods=['POST'])
def task_update():
    task = request.json
    print(task)
    return '', 200
