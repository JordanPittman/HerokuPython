from flask import Flask, request, redirect, render_template_string, url_for, g
import sqlite3

app = Flask(__name__)

DATABASE = 'database.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS entries (id INTEGER PRIMARY KEY, random_string TEXT)')
        db.commit()

@app.route('/')
def index():
    return 'Welcome to the Flask app!'

@app.route('/dbinput')
def db_input():
    return '''
    <form method="post" action="/submit">
        Enter string: <input type="text" name="randomString" required>
        <button type="submit">Submit</button>
    </form>
    '''

@app.route('/submit', methods=['POST'])
def submit():
    random_string = request.form['randomString']
    db = get_db()
    cursor = db.cursor()
    cursor.execute('INSERT INTO entries (random_string) VALUES (?)', (random_string,))
    db.commit()
    return redirect(url_for('db'))

@app.route('/db')
def db():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT id, random_string FROM entries')
    entries = cursor.fetchall()
    return '<br>'.join(f'ID: {entry[0]}, String: {entry[1]}' for entry in entries)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
