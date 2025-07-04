import pytest
from app import app, get_db_connection


# Fixture to set up test database
@pytest.fixture
def client():
    # Use in-memory database for tests
    app.config['DATABASE'] = 'file:test_expense.db?mode=memory&cache=shared'
    app.config['TESTING'] = True

    # Initialize test database
    with app.app_context():
        conn = get_db_connection()
        # Read schema file directly since app.open_resource may not work in tests
        with open('schema.sql', 'r') as f:
            conn.executescript(f.read())
        conn.commit()

    # Create test client
    with app.test_client() as client:
        yield client

    # Clean up after tests
    with app.app_context():
        conn = get_db_connection()
        conn.execute('DROP TABLE IF EXISTS expense')
        conn.execute('DROP TABLE IF EXISTS expense_category')
        conn.commit()
        conn.close()


# Test database initialization
def test_database_initialization(client):
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        assert 'expense_category' in tables


# Test adding a new category
def test_add_category(client):
    response = client.post('/add', data={
        'name': 'Test Category',
        'description': 'Test Description'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Test Category' in response.data
    assert b'Test Description' in response.data


# Test editing an existing category
def test_edit_category(client):
    # First add a category
    client.post('/add', data={
        'name': 'Original Category',
        'description': 'Original Description'
    })

    # Edit the category
    response = client.post('/edit/1', data={
        'name': 'Updated Category',
        'description': 'Updated Description'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Updated Category' in response.data
    assert b'Updated Description' in response.data
    assert b'Original Category' not in response.data


# Test deleting a category
def test_delete_category(client):
    # Add a category
    client.post('/add', data={
        'name': 'To Be Deleted',
        'description': 'Will be removed'
    })

    # Verify the category was added
    response = client.get('/add')
    assert b'To Be Deleted' in response.data
    assert b'Will be removed' in response.data

    # Delete the category
    response = client.get('/delete/1', follow_redirects=True)

    # Verify the deletion was successful
    assert response.status_code == 200
    assert b'To Be Deleted' not in response.data
    assert b'Will be removed' not in response.data


# Test deleting a non-existent category
def test_delete_nonexistent_category(client):
    # Try to delete a category that doesn't exist
    response = client.get('/delete/999', follow_redirects=True)

    # Should still redirect successfully (no error handling in current implementation)
    assert response.status_code == 200


# Test category listing
def test_category_listing(client):
    # Add multiple categories
    categories = [
        {'name': 'Category 1', 'description': 'Desc 1'},
        {'name': 'Category 2', 'description': 'Desc 2'},
        {'name': 'Category 3', 'description': 'Desc 3'}
    ]

    for category in categories:
        client.post('/add', data=category)

    response = client.get('/add')
    for category in categories:
        assert category['name'].encode() in response.data
        assert category['description'].encode() in response.data


# Test form validation
def test_form_validation(client):
    # Test missing name
    response = client.post('/add', data={
        'name': '',
        'description': 'Should fail'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Category Name is required' in response.data


# Test expense functionality
def test_add_expense(client):
    # First add a category
    client.post('/add', data={
        'name': 'Test Category',
        'description': 'Test Description'
    })

    # Add an expense
    response = client.post('/expenses/add', data={
        'date': '2024-01-15',
        'description': 'Test Expense',
        'vendor': 'Test Vendor',
        'category_id': '1',
        'amount': '25.50'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Test Expense' in response.data
    assert b'Test Vendor' in response.data
    assert b'25.50' in response.data


def test_edit_expense(client):
    # Add category and expense
    client.post('/add', data={
        'name': 'Test Category',
        'description': 'Test Description'
    })
    client.post('/expenses/add', data={
        'date': '2024-01-15',
        'description': 'Original Expense',
        'vendor': 'Original Vendor',
        'category_id': '1',
        'amount': '10.00'
    })

    # Edit the expense
    response = client.post('/expenses/edit/1', data={
        'date': '2024-01-16',
        'description': 'Updated Expense',
        'vendor': 'Updated Vendor',
        'category_id': '1',
        'amount': '15.75'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Updated Expense' in response.data
    assert b'Updated Vendor' in response.data
    assert b'15.75' in response.data
    assert b'Original Expense' not in response.data


def test_delete_expense(client):
    # Add category and expense
    client.post('/add', data={
        'name': 'Test Category',
        'description': 'Test Description'
    })
    client.post('/expenses/add', data={
        'date': '2024-01-15',
        'description': 'To Be Deleted',
        'vendor': 'Test Vendor',
        'category_id': '1',
        'amount': '20.00'
    })

    # Verify expense exists
    response = client.get('/expenses')
    assert b'To Be Deleted' in response.data

    # Delete the expense
    response = client.get('/expenses/delete/1', follow_redirects=True)
    assert response.status_code == 200
    assert b'To Be Deleted' not in response.data


def test_expense_validation(client):
    # Add a category first
    client.post('/add', data={
        'name': 'Test Category',
        'description': 'Test Description'
    })

    # Test missing required fields
    response = client.post('/expenses/add', data={
        'date': '',
        'description': 'Test',
        'category_id': '1',
        'amount': '10.00'
    }, follow_redirects=True)
    assert b'Date is required' in response.data

    response = client.post('/expenses/add', data={
        'date': '2024-01-15',
        'description': '',
        'category_id': '1',
        'amount': '10.00'
    }, follow_redirects=True)
    assert b'Description is required' in response.data

    response = client.post('/expenses/add', data={
        'date': '2024-01-15',
        'description': 'Test',
        'category_id': '',
        'amount': '10.00'
    }, follow_redirects=True)
    assert b'Category is required' in response.data

    response = client.post('/expenses/add', data={
        'date': '2024-01-15',
        'description': 'Test',
        'category_id': '1',
        'amount': ''
    }, follow_redirects=True)
    assert b'Amount is required' in response.data

    # Test invalid amount
    response = client.post('/expenses/add', data={
        'date': '2024-01-15',
        'description': 'Test',
        'category_id': '1',
        'amount': 'invalid'
    }, follow_redirects=True)
    assert b'Amount must be a valid number' in response.data
