"""Tests for user service operations."""
import pytest
from app import create_app
from database.db import db


@pytest.fixture(autouse=True)
def reset_db():
    """Reset the database before each test."""
    db.reset()
    yield
    db.reset()


@pytest.fixture
def app():
    return create_app(testing=True)


@pytest.fixture
def client(app):
    return app.test_client()


class TestAddUser:
    def test_add_valid_student(self):
        from app.services.library_service import library_service
        result = library_service.add_user({
            'user_id': 'U200', 'name': 'Test Student',
            'email': 'test@uni.edu', 'role': 'Student',
        })
        assert result['success'] is True
        assert result['code'] == 201
        assert result['user']['user_id'] == 'U200'
        assert result['user']['role'] == 'Student'
        assert result['user']['active_loans'] == 0

    def test_add_valid_faculty(self):
        from app.services.library_service import library_service
        result = library_service.add_user({
            'user_id': 'U201', 'name': 'Prof Test',
            'email': 'prof@uni.edu', 'role': 'Faculty',
        })
        assert result['success'] is True
        assert result['user']['role'] == 'Faculty'

    def test_add_duplicate_user(self):
        from app.services.library_service import library_service
        library_service.add_user({
            'user_id': 'U200', 'name': 'A', 'email': 'a@b.com', 'role': 'Student',
        })
        result = library_service.add_user({
            'user_id': 'U200', 'name': 'B', 'email': 'b@b.com', 'role': 'Faculty',
        })
        assert result['success'] is False
        assert result['code'] == 409
        assert 'already exists' in result['error']

    def test_add_user_missing_user_id(self):
        from app.services.library_service import library_service
        result = library_service.add_user({'name': 'X', 'email': 'x@x.com', 'role': 'Student'})
        assert result['success'] is False
        assert result['code'] == 400
        assert 'user_id' in result['error']

    def test_add_user_missing_name(self):
        from app.services.library_service import library_service
        result = library_service.add_user({'user_id': 'U200', 'email': 'x@x.com', 'role': 'Student'})
        assert result['success'] is False
        assert result['code'] == 400
        assert 'name' in result['error']

    def test_add_user_missing_email(self):
        from app.services.library_service import library_service
        result = library_service.add_user({'user_id': 'U200', 'name': 'X', 'role': 'Student'})
        assert result['success'] is False
        assert result['code'] == 400
        assert 'email' in result['error']

    def test_add_user_invalid_role(self):
        from app.services.library_service import library_service
        result = library_service.add_user({
            'user_id': 'U200', 'name': 'X', 'email': 'x@x.com', 'role': 'Admin',
        })
        assert result['success'] is False
        assert result['code'] == 400

    def test_add_user_empty_strings(self):
        from app.services.library_service import library_service
        result = library_service.add_user({
            'user_id': '', 'name': '', 'email': '', 'role': 'Student',
        })
        assert result['success'] is False
        assert result['code'] == 400


class TestGetUser:
    def test_get_seeded_user(self):
        from app.services.library_service import library_service
        result = library_service.get_user('U101')
        assert result['success'] is True
        assert result['user']['name'] == 'Alice Johnson'

    def test_get_nonexistent_user(self):
        from app.services.library_service import library_service
        result = library_service.get_user('U999')
        assert result['success'] is False
        assert result['code'] == 404

    def test_get_all_users_returns_seeded(self):
        from app.services.library_service import library_service
        result = library_service.get_all_users()
        assert result['success'] is True
        assert len(result['users']) >= 2


class TestDeleteUser:
    def test_delete_user_no_loans(self):
        from app.services.library_service import library_service
        library_service.add_user({
            'user_id': 'U300', 'name': 'Del User',
            'email': 'del@x.com', 'role': 'Student',
        })
        result = library_service.delete_user('U300')
        assert result['success'] is True
        assert result['code'] == 200

    def test_delete_nonexistent_user(self):
        from app.services.library_service import library_service
        result = library_service.delete_user('U999')
        assert result['success'] is False
        assert result['code'] == 404

    def test_delete_user_with_active_loan(self):
        from app.services.library_service import library_service
        library_service.borrow_book('U101', 'B001')
        result = library_service.delete_user('U101')
        assert result['success'] is False
        assert result['code'] == 409
        assert 'active loan' in result['error'].lower()

    def test_delete_confirms_removal(self):
        from app.services.library_service import library_service
        library_service.add_user({
            'user_id': 'U300', 'name': 'Temp', 'email': 't@x.com', 'role': 'Student',
        })
        library_service.delete_user('U300')
        result = library_service.get_user('U300')
        assert result['success'] is False
