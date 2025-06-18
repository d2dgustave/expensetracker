from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('expense.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/add', methods=('GET', 'POST'))
def add_category():
    conn = get_db_connection()
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        conn.execute(
            'INSERT INTO expense_category (name, description) VALUES (?, ?)',
            (name, description)
        )
        conn.commit()
    categories = conn.execute('SELECT * FROM expense_category').fetchall()
    conn.close()
    return render_template('add_category.html', categories=categories)

if __name__ == '__main__':
    # app.run(debug=False)
    app.run(debug=False)
