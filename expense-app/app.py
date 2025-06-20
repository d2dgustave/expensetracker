import os
from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)
app.config['DATABASE'] = os.environ.get('DATABASE_URL', 'expense.db')

def get_db_connection():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/add', methods=('GET', 'POST'))
def add_category():
    conn = get_db_connection()
    error = None
    
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        
        # Validate inputs
        if not name:
            error = 'Category Name is required'
        else:
            conn.execute(
                'INSERT INTO expense_category (name, description) VALUES (?, ?)',
                (name, description)
            )
            conn.commit()
    
    categories = conn.execute('SELECT * FROM expense_category').fetchall()
    conn.close()
    return render_template('add_category.html', categories=categories, error=error)


# Add these routes after your existing routes
@app.route('/edit/<int:id>', methods=('GET', 'POST'))
def edit_category(id):
    conn = get_db_connection()
    category = conn.execute('SELECT * FROM expense_category WHERE id = ?', (id,)).fetchone()
    if category is None:
        conn.close()
        return "Category not found", 404
 
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        
        conn.execute(
            'UPDATE expense_category SET name = ?, description = ? WHERE id = ?',
            (name, description, id)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('add_category'))
    
    conn.close()
    return render_template('edit_category.html', category=category)



if __name__ == '__main__':
    app.run(debug=True)
    # app.run(debug=False)
