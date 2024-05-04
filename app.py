from flask import Flask, request, redirect, render_template_string, url_for, g
import psycopg2
import os

app = Flask(__name__)

DATABASE_URL = os.environ['DATABASE_URL']  # Environment variable provided by Railway

def get_db():
    if 'db' not in g:
        g.db = psycopg2.connect(DATABASE_URL, sslmode='require')
    return g.db

@app.teardown_appcontext
def close_connection(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS entries (id SERIAL PRIMARY KEY, random_string TEXT)')
        db.commit()
        cursor.close()

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
    cursor.execute('INSERT INTO entries (random_string) VALUES (%s)', (random_string,))
    db.commit()
    cursor.close()
    return redirect(url_for('db'))

@app.route('/db')
def db():
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute('SELECT id, random_string FROM entries')
        entries = cursor.fetchall()
        return '<br>'.join(f'ID: {entry[0]}, String: {entry[1]}' for entry in entries)
    except Exception as e:
        return f"An error occurred: {str(e)}"  # To handle and display errors more effectively
    finally:
        cursor.close()

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
