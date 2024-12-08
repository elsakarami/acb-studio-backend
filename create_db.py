import sqlite3
from flask import Flask

app = Flask(__name__)

def create_table():
    conn = sqlite3.connect('db/users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  email TEXT UNIQUE NOT NULL,
                  password TEXT NOT NULL)''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return "Welcome to the ACB test!"

if __name__ == '__main__':
    create_table()
    app.run(debug=True)