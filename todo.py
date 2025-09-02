import git
import os
import sqlite3

from bottle import Bottle, template, run
from bottle import (request)
from bottle import redirect
from bottle import TEMPLATE_PATH
import os

TEMPLATE_PATH.append(os.path.join(os.path.dirname(__file__), 'views'))

app = Bottle()
db_path = os.path.join(os.path.dirname(__file__), 'todo.db')

@app.route('/')
def index():
    redirect('/todo')


@app.get('/todo')
def todo_list():
    show  = request.query.show or 'open'
    match show:
        case 'open':
            db_query = "SELECT id, task FROM todo WHERE status LIKE '1'"
        case 'closed':
            db_query = "SELECT id, task FROM todo WHERE status LIKE '0'"
        case 'all':
            db_query = "SELECT id, task FROM todo"
        case _:
            return template('message.tpl',
                message = 'Wrong query parameter: show must be either open, closed or all.')
    with sqlite3.connect(db_path) as connection:
        cursor = connection.cursor()
        cursor.execute(db_query)
        result = cursor.fetchall()
    output = template('show_tasks.tpl', rows=result)
    return output

@app.route('/new', method=['GET', 'POST'])
def new_task():
    if request.POST:
        new_task = request.forms.task.strip()
        with sqlite3.connect(db_path) as connection:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO todo (task,status) VALUES (?,?)", (new_task, 1))
            new_id = cursor.lastrowid
        return template('message.tpl',
            message=f'The new task was inserted into the database, the ID is {new_id}')
    else:
        return template('new_task.tpl')

@app.route('/edit/<number:int>', method=['GET', 'POST'])
def edit_task(number):
    if request.POST:
        new_data = request.forms.task.strip()
        status = request.forms.status.strip()
        if status == 'open':
            status = 1
        else:
            status = 0
        with sqlite3.connect(db_path) as connection:
            cursor = connection.cursor()
            cursor.execute("UPDATE todo SET task = ?, status = ? WHERE id LIKE ?", (new_data, status, number))
        return template('message.tpl',
            message=f'The task number {number} was successfully updated')
    else:
        with sqlite3.connect(db_path) as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT task FROM todo WHERE id LIKE ?", (number,))
            current_data = cursor.fetchone()
        return template('edit_task', current_data=current_data, number=number)

@app.route('/as_json/<number:re:[0-9]+>')
def task_as_json(number):
    with sqlite3.connect(db_path) as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT id, task, status FROM todo WHERE id LIKE ?", (number,))
        result = cursor.fetchone()
    if not result:
        return {'task': 'This task ID number does not exist!'}
    else:
        return {'id': result[0], 'task': result[1], 'status': result[2]}

@app.route('/update_server')
def update_server():
    try:
        repo = git.Repo('/home/pierrickviret74/bottle_venv')
        origin = repo.remotes.origin
        origin.pull()
        return template('message.tpl', message='Server updated successfully!')
    except Exception as e:
        return template('message.tpl', message=f'Update failed: {str(e)}')


application = app

if __name__ == '__main__':
    run(app, host='localhost', port=8080)