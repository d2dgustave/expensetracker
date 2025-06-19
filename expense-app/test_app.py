import os
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
        with app.open_resource('schema.sql') as f:
            conn.executescript(f.read().decode('utf8'))
        conn.commit()
    
    # Create test client
    with app.test_client() as client:
        yield client
    
    # Clean up after tests
    with app.app_context():
        conn = get_db_connection()
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
#def test_delete_category(client):
    # Add a category
#    client.post('/add', data={
#        'name': 'To Be Deleted',
#        'description': 'Will be removed'
#    })
    
    # Delete the category
#    response = client.get('/delete/1', follow_redirects=True)
    
#    assert response.status_code == 200
#    assert b'To Be Deleted' not in response.data
#    assert b'Will be removed' not in response.data

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
    
    assert b'Category Name is required' in response.data
