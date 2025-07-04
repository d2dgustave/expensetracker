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
    categories = []
    
    try:
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
    except Exception as e:
        error = f"Database error: {str(e)}"
    finally:
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

@app.route('/delete/<int:id>')
def delete_category(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM expense_category WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('add_category'))

# Expense management routes
@app.route('/')
@app.route('/expenses')
def list_expenses():
    conn = get_db_connection()
    expenses = conn.execute('''
        SELECT e.id, e.date, e.description, e.vendor, e.amount, 
               ec.name as category_name
        FROM expense e
        JOIN expense_category ec ON e.category_id = ec.id
        ORDER BY e.date DESC
    ''').fetchall()
    conn.close()
    return render_template('list_expenses.html', expenses=expenses)

@app.route('/expenses/add', methods=('GET', 'POST'))
def add_expense():
    conn = get_db_connection()
    error = None
    
    if request.method == 'POST':
        date = request.form.get('date', '').strip()
        description = request.form.get('description', '').strip()
        vendor = request.form.get('vendor', '').strip()
        category_id = request.form.get('category_id', '').strip()
        amount = request.form.get('amount', '').strip()
        
        # Validate inputs
        if not date:
            error = 'Date is required'
        elif not description:
            error = 'Description is required'
        elif not category_id:
            error = 'Category is required'
        elif not amount:
            error = 'Amount is required'
        else:
            try:
                float(amount)
                conn.execute(
                    'INSERT INTO expense (date, description, vendor, category_id, amount) VALUES (?, ?, ?, ?, ?)',
                    (date, description, vendor, category_id, amount)
                )
                conn.commit()
                conn.close()
                return redirect(url_for('list_expenses'))
            except ValueError:
                error = 'Amount must be a valid number'
    
    categories = conn.execute('SELECT * FROM expense_category ORDER BY name').fetchall()
    conn.close()
    return render_template('add_expense.html', categories=categories, error=error)

@app.route('/expenses/edit/<int:id>', methods=('GET', 'POST'))
def edit_expense(id):
    conn = get_db_connection()
    expense = conn.execute('SELECT * FROM expense WHERE id = ?', (id,)).fetchone()
    if expense is None:
        conn.close()
        return "Expense not found", 404
 
    if request.method == 'POST':
        date = request.form['date']
        description = request.form['description']
        vendor = request.form['vendor']
        category_id = request.form['category_id']
        amount = request.form['amount']
        
        try:
            float(amount)
            conn.execute(
                'UPDATE expense SET date = ?, description = ?, vendor = ?, category_id = ?, amount = ? WHERE id = ?',
                (date, description, vendor, category_id, amount, id)
            )
            conn.commit()
            conn.close()
            return redirect(url_for('list_expenses'))
        except ValueError:
            conn.close()
            return "Amount must be a valid number", 400
    
    categories = conn.execute('SELECT * FROM expense_category ORDER BY name').fetchall()
    conn.close()
    return render_template('edit_expense.html', expense=expense, categories=categories)

@app.route('/expenses/delete/<int:id>')
def delete_expense(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM expense WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('list_expenses'))

if __name__ == '__main__':
    app.run(debug=True)
    # app.run(debug=False)
