"""Integration tests for REST API endpoints."""
import json
import pytest
from app import create_app
from database.db import db


@pytest.fixture(autouse=True)
def reset_db():
    db.reset()
    yield
    db.reset()


@pytest.fixture
def app():
    return create_app(testing=True)


@pytest.fixture
def client(app):
    return app.test_client()


def post_json(client, url, data):
    return client.post(url, data=json.dumps(data), content_type='application/json')


def delete(client, url):
    return client.delete(url)


class TestHealthEndpoint:
    def test_health_returns_200(self, client):
        r = client.get('/api/health')
        assert r.status_code == 200

    def test_health_response_structure(self, client):
        r = client.get('/api/health')
        data = r.get_json()
        assert data['status'] == 'UP'
        assert data['service'] == 'Enterprise Smart Library Management Platform'
        assert data['version'] == '1.0.0'


class TestUsersEndpoint:
    def test_create_user_201(self, client):
        r = post_json(client, '/api/users', {
            'user_id': 'U200', 'name': 'Grace Hopper',
            'email': 'grace@navy.mil', 'role': 'Faculty',
        })
        assert r.status_code == 201
        data = r.get_json()
        assert data['user']['user_id'] == 'U200'

    def test_create_user_duplicate_409(self, client):
        post_json(client, '/api/users', {
            'user_id': 'U200', 'name': 'A', 'email': 'a@b.com', 'role': 'Student',
        })
        r = post_json(client, '/api/users', {
            'user_id': 'U200', 'name': 'B', 'email': 'b@b.com', 'role': 'Faculty',
        })
        assert r.status_code == 409

    def test_create_user_invalid_400(self, client):
        r = post_json(client, '/api/users', {'name': 'No ID'})
        assert r.status_code == 400

    def test_get_user_200(self, client):
        r = client.get('/api/users/U101')
        assert r.status_code == 200
        assert r.get_json()['user']['name'] == 'Alice Johnson'

    def test_get_user_not_found_404(self, client):
        r = client.get('/api/users/U999')
        assert r.status_code == 404
        assert 'error' in r.get_json()

    def test_get_all_users_200(self, client):
        r = client.get('/api/users')
        assert r.status_code == 200
        data = r.get_json()
        assert 'users' in data
        assert len(data['users']) >= 2

    def test_delete_user_200(self, client):
        post_json(client, '/api/users', {
            'user_id': 'U300', 'name': 'Del', 'email': 'd@d.com', 'role': 'Student',
        })
        r = delete(client, '/api/users/U300')
        assert r.status_code == 200

    def test_delete_user_not_found_404(self, client):
        r = delete(client, '/api/users/U999')
        assert r.status_code == 404

    def test_delete_user_with_active_loan_409(self, client):
        post_json(client, '/api/borrow', {'user_id': 'U101', 'book_id': 'B001'})
        r = delete(client, '/api/users/U101')
        assert r.status_code == 409
        assert 'error' in r.get_json()


class TestBooksEndpoint:
    def test_get_all_books_200(self, client):
        r = client.get('/api/books')
        assert r.status_code == 200
        data = r.get_json()
        assert 'books' in data
        assert len(data['books']) >= 2

    def test_search_books_with_query(self, client):
        r = client.get('/api/books?q=devops')
        assert r.status_code == 200
        data = r.get_json()
        assert len(data['books']) >= 1

    def test_search_books_empty_query(self, client):
        r = client.get('/api/books?q=')
        assert r.status_code == 200
        data = r.get_json()
        assert len(data['books']) >= 2

    def test_search_books_no_results(self, client):
        r = client.get('/api/books?q=zzznoresult')
        assert r.status_code == 200
        assert len(r.get_json()['books']) == 0

    def test_create_book_201(self, client):
        r = post_json(client, '/api/books', {
            'book_id': 'B100', 'title': 'Python Engineering',
            'author': 'Example Author', 'isbn': '123456789', 'total_copies': 5,
        })
        assert r.status_code == 201
        assert r.get_json()['book']['book_id'] == 'B100'

    def test_create_book_duplicate_409(self, client):
        post_json(client, '/api/books', {
            'book_id': 'B100', 'title': 'T', 'author': 'A', 'isbn': '1', 'total_copies': 1,
        })
        r = post_json(client, '/api/books', {
            'book_id': 'B100', 'title': 'T2', 'author': 'A2', 'isbn': '2', 'total_copies': 1,
        })
        assert r.status_code == 409

    def test_create_book_invalid_400(self, client):
        r = post_json(client, '/api/books', {'title': 'No ID'})
        assert r.status_code == 400

    def test_get_book_200(self, client):
        r = client.get('/api/books/B001')
        assert r.status_code == 200
        assert r.get_json()['book']['book_id'] == 'B001'

    def test_get_book_not_found_404(self, client):
        r = client.get('/api/books/B999')
        assert r.status_code == 404


class TestBorrowEndpoint:
    def test_borrow_success_201(self, client):
        r = post_json(client, '/api/borrow', {'user_id': 'U101', 'book_id': 'B001'})
        assert r.status_code == 201
        data = r.get_json()
        assert data['loan']['status'] == 'ACTIVE'

    def test_borrow_missing_fields_400(self, client):
        r = post_json(client, '/api/borrow', {'user_id': 'U101'})
        assert r.status_code == 400

    def test_borrow_invalid_user_404(self, client):
        r = post_json(client, '/api/borrow', {'user_id': 'U999', 'book_id': 'B001'})
        assert r.status_code == 404

    def test_borrow_invalid_book_404(self, client):
        r = post_json(client, '/api/borrow', {'user_id': 'U101', 'book_id': 'B999'})
        assert r.status_code == 404

    def test_borrow_out_of_stock_409(self, client):
        # Exhaust all 3 copies of B002
        post_json(client, '/api/users', {
            'user_id': 'U200', 'name': 'X', 'email': 'x@x.com', 'role': 'Faculty',
        })
        post_json(client, '/api/users', {
            'user_id': 'U201', 'name': 'Y', 'email': 'y@x.com', 'role': 'Faculty',
        })
        post_json(client, '/api/borrow', {'user_id': 'U101', 'book_id': 'B002'})
        post_json(client, '/api/borrow', {'user_id': 'U102', 'book_id': 'B002'})
        post_json(client, '/api/borrow', {'user_id': 'U200', 'book_id': 'B002'})
        r = post_json(client, '/api/borrow', {'user_id': 'U201', 'book_id': 'B002'})
        assert r.status_code == 409
        assert 'error' in r.get_json()


class TestReturnEndpoint:
    def test_return_success_200(self, client):
        post_json(client, '/api/borrow', {'user_id': 'U101', 'book_id': 'B001'})
        r = post_json(client, '/api/return', {'user_id': 'U101', 'book_id': 'B001'})
        assert r.status_code == 200
        assert r.get_json()['loan']['status'] == 'RETURNED'

    def test_return_missing_fields_400(self, client):
        r = post_json(client, '/api/return', {'user_id': 'U101'})
        assert r.status_code == 400

    def test_return_no_active_loan_404(self, client):
        r = post_json(client, '/api/return', {'user_id': 'U101', 'book_id': 'B001'})
        assert r.status_code == 404

    def test_return_invalid_user_404(self, client):
        r = post_json(client, '/api/return', {'user_id': 'U999', 'book_id': 'B001'})
        assert r.status_code == 404


class TestLoansEndpoint:
    def test_get_loans_200(self, client):
        r = client.get('/api/loans')
        assert r.status_code == 200
        assert 'loans' in r.get_json()

    def test_get_loans_after_borrow(self, client):
        post_json(client, '/api/borrow', {'user_id': 'U101', 'book_id': 'B001'})
        r = client.get('/api/loans')
        loans = r.get_json()['loans']
        assert len(loans) == 1
        assert loans[0]['status'] == 'ACTIVE'


class TestDashboardEndpoint:
    def test_dashboard_200(self, client):
        r = client.get('/api/dashboard')
        assert r.status_code == 200
        data = r.get_json()
        assert 'total_books' in data
        assert 'available_copies' in data
        assert 'total_users' in data
        assert 'active_loans' in data
        assert 'returned_loans' in data


class TestFrontendRoutes:
    def test_dashboard_page_loads(self, client):
        r = client.get('/')
        assert r.status_code == 200

    def test_books_page_loads(self, client):
        r = client.get('/books')
        assert r.status_code == 200

    def test_users_page_loads(self, client):
        r = client.get('/users')
        assert r.status_code == 200

    def test_loans_page_loads(self, client):
        r = client.get('/loans')
        assert r.status_code == 200
