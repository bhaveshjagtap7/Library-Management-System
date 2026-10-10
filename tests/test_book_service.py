"""Tests for book service operations."""
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


class TestAddBook:
    def test_add_valid_book(self):
        from app.services.library_service import library_service
        result = library_service.add_book({
            'book_id': 'B100', 'title': 'Test Book', 'author': 'Author',
            'isbn': '000-0000000001', 'total_copies': 3,
        })
        assert result['success'] is True
        assert result['code'] == 201
        assert result['book']['book_id'] == 'B100'
        assert result['book']['total_copies'] == 3
        assert result['book']['available_copies'] == 3

    def test_add_duplicate_book(self):
        from app.services.library_service import library_service
        library_service.add_book({
            'book_id': 'B100', 'title': 'T', 'author': 'A',
            'isbn': '111', 'total_copies': 1,
        })
        result = library_service.add_book({
            'book_id': 'B100', 'title': 'T2', 'author': 'A2',
            'isbn': '222', 'total_copies': 1,
        })
        assert result['success'] is False
        assert result['code'] == 409

    def test_add_book_missing_book_id(self):
        from app.services.library_service import library_service
        result = library_service.add_book({
            'title': 'T', 'author': 'A', 'isbn': '111', 'total_copies': 1,
        })
        assert result['success'] is False
        assert result['code'] == 400
        assert 'book_id' in result['error']

    def test_add_book_missing_title(self):
        from app.services.library_service import library_service
        result = library_service.add_book({
            'book_id': 'B100', 'author': 'A', 'isbn': '111', 'total_copies': 1,
        })
        assert result['success'] is False
        assert result['code'] == 400
        assert 'title' in result['error']

    def test_add_book_missing_author(self):
        from app.services.library_service import library_service
        result = library_service.add_book({
            'book_id': 'B100', 'title': 'T', 'isbn': '111', 'total_copies': 1,
        })
        assert result['success'] is False
        assert result['code'] == 400
        assert 'author' in result['error']

    def test_add_book_missing_isbn(self):
        from app.services.library_service import library_service
        result = library_service.add_book({
            'book_id': 'B100', 'title': 'T', 'author': 'A', 'total_copies': 1,
        })
        assert result['success'] is False
        assert result['code'] == 400
        assert 'isbn' in result['error']

    def test_add_book_zero_copies(self):
        from app.services.library_service import library_service
        result = library_service.add_book({
            'book_id': 'B100', 'title': 'T', 'author': 'A',
            'isbn': '111', 'total_copies': 0,
        })
        assert result['success'] is False
        assert result['code'] == 400

    def test_add_book_negative_copies(self):
        from app.services.library_service import library_service
        result = library_service.add_book({
            'book_id': 'B100', 'title': 'T', 'author': 'A',
            'isbn': '111', 'total_copies': -1,
        })
        assert result['success'] is False
        assert result['code'] == 400

    def test_add_book_invalid_copies_type(self):
        from app.services.library_service import library_service
        result = library_service.add_book({
            'book_id': 'B100', 'title': 'T', 'author': 'A',
            'isbn': '111', 'total_copies': 'many',
        })
        assert result['success'] is False
        assert result['code'] == 400


class TestGetBook:
    def test_get_seeded_book(self):
        from app.services.library_service import library_service
        result = library_service.get_book('B001')
        assert result['success'] is True
        assert result['book']['title'] == 'Cloud Native DevOps Architecture'

    def test_get_nonexistent_book(self):
        from app.services.library_service import library_service
        result = library_service.get_book('B999')
        assert result['success'] is False
        assert result['code'] == 404

    def test_book_status_available(self):
        from app.services.library_service import library_service
        result = library_service.get_book('B001')
        assert result['book']['status'] == 'Available'


class TestSearchBooks:
    def test_empty_query_returns_all(self):
        from app.services.library_service import library_service
        result = library_service.search_books('')
        assert result['success'] is True
        assert len(result['books']) >= 2

    def test_search_by_title_case_insensitive(self):
        from app.services.library_service import library_service
        result = library_service.search_books('CLOUD NATIVE')
        assert result['success'] is True
        assert any(b['book_id'] == 'B001' for b in result['books'])

    def test_search_by_author(self):
        from app.services.library_service import library_service
        result = library_service.search_books('torvalds')
        assert result['success'] is True
        assert any(b['book_id'] == 'B001' for b in result['books'])

    def test_search_by_isbn(self):
        from app.services.library_service import library_service
        result = library_service.search_books('978-0134685991')
        assert result['success'] is True
        assert any(b['book_id'] == 'B001' for b in result['books'])

    def test_search_no_results(self):
        from app.services.library_service import library_service
        result = library_service.search_books('zzzznonexistent')
        assert result['success'] is True
        assert len(result['books']) == 0

    def test_search_partial_title(self):
        from app.services.library_service import library_service
        result = library_service.search_books('devops')
        assert result['success'] is True
        assert len(result['books']) >= 1

    def test_search_by_delivery_author_partial(self):
        from app.services.library_service import library_service
        result = library_service.search_books('humble')
        assert result['success'] is True
        assert any(b['book_id'] == 'B002' for b in result['books'])
