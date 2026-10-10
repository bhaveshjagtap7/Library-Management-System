"""Tests for borrow and return operations."""
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
def svc():
    from app.services.library_service import library_service
    return library_service


class TestBorrowBook:
    def test_successful_borrow(self, svc):
        result = svc.borrow_book('U101', 'B001')
        assert result['success'] is True
        assert result['code'] == 201
        assert result['loan']['status'] == 'ACTIVE'
        assert result['loan']['user_id'] == 'U101'
        assert result['loan']['book_id'] == 'B001'
        assert result['loan']['returned_at'] is None

    def test_borrow_decrements_available_copies(self, svc):
        initial = db.books['B001'].available_copies
        svc.borrow_book('U101', 'B001')
        assert db.books['B001'].available_copies == initial - 1

    def test_borrow_increments_user_active_loans(self, svc):
        svc.borrow_book('U101', 'B001')
        assert db.users['U101'].active_loans == 1

    def test_borrow_creates_active_loan(self, svc):
        result = svc.borrow_book('U101', 'B001')
        loan_id = result['loan']['loan_id']
        assert loan_id in db.loans
        assert db.loans[loan_id]['status'] == 'ACTIVE'

    def test_borrow_loan_id_format(self, svc):
        result = svc.borrow_book('U101', 'B001')
        assert result['loan']['loan_id'].startswith('L-')

    def test_borrow_nonexistent_user(self, svc):
        result = svc.borrow_book('U999', 'B001')
        assert result['success'] is False
        assert result['code'] == 404

    def test_borrow_nonexistent_book(self, svc):
        result = svc.borrow_book('U101', 'B999')
        assert result['success'] is False
        assert result['code'] == 404

    def test_borrow_out_of_stock(self, svc):
        # Exhaust all copies of B002 (3 copies)
        svc.add_user({'user_id': 'U200', 'name': 'A', 'email': 'a@x.com', 'role': 'Faculty'})
        svc.add_user({'user_id': 'U201', 'name': 'B', 'email': 'b@x.com', 'role': 'Faculty'})
        svc.borrow_book('U101', 'B002')
        svc.borrow_book('U102', 'B002')
        svc.borrow_book('U200', 'B002')
        result = svc.borrow_book('U201', 'B002')
        assert result['success'] is False
        assert result['code'] == 409
        assert 'out of stock' in result['error'].lower()

    def test_student_quota_3_loans(self, svc):
        # Add extra books to test quota
        svc.add_book({'book_id': 'B010', 'title': 'T1', 'author': 'A', 'isbn': '1', 'total_copies': 5})
        svc.add_book({'book_id': 'B011', 'title': 'T2', 'author': 'A', 'isbn': '2', 'total_copies': 5})
        svc.add_book({'book_id': 'B012', 'title': 'T3', 'author': 'A', 'isbn': '3', 'total_copies': 5})
        svc.borrow_book('U101', 'B001')
        svc.borrow_book('U101', 'B010')
        svc.borrow_book('U101', 'B011')
        # 4th borrow should fail for Student
        result = svc.borrow_book('U101', 'B012')
        assert result['success'] is False
        assert result['code'] == 409
        assert 'limit' in result['error'].lower()

    def test_faculty_quota_5_loans(self, svc):
        for i in range(5):
            svc.add_book({
                'book_id': f'BF0{i}', 'title': f'Book {i}',
                'author': 'A', 'isbn': str(i), 'total_copies': 2,
            })
        for i in range(5):
            r = svc.borrow_book('U102', f'BF0{i}')
            assert r['success'] is True
        # 6th borrow should fail
        svc.add_book({'book_id': 'BF05', 'title': 'Extra', 'author': 'A', 'isbn': '99', 'total_copies': 2})
        result = svc.borrow_book('U102', 'BF05')
        assert result['success'] is False
        assert result['code'] == 409

    def test_inventory_never_negative(self, svc):
        # B002 has 3 copies — ensure available_copies >= 0
        svc.add_user({'user_id': 'U200', 'name': 'C', 'email': 'c@x.com', 'role': 'Faculty'})
        svc.borrow_book('U101', 'B002')
        svc.borrow_book('U102', 'B002')
        svc.borrow_book('U200', 'B002')
        assert db.books['B002'].available_copies == 0
        svc.borrow_book('U200', 'B002')  # already borrowed & out of stock — should fail
        assert db.books['B002'].available_copies >= 0

    def test_borrow_generates_sequential_loan_ids(self, svc):
        r1 = svc.borrow_book('U101', 'B001')
        r2 = svc.borrow_book('U102', 'B002')
        id1 = r1['loan']['loan_id']
        id2 = r2['loan']['loan_id']
        num1 = int(id1.split('-')[1])
        num2 = int(id2.split('-')[1])
        assert num2 == num1 + 1


class TestReturnBook:
    def test_successful_return(self, svc):
        svc.borrow_book('U101', 'B001')
        result = svc.return_book('U101', 'B001')
        assert result['success'] is True
        assert result['loan']['status'] == 'RETURNED'
        assert result['loan']['returned_at'] is not None

    def test_return_restores_inventory(self, svc):
        initial = db.books['B001'].available_copies
        svc.borrow_book('U101', 'B001')
        svc.return_book('U101', 'B001')
        assert db.books['B001'].available_copies == initial

    def test_return_decrements_user_active_loans(self, svc):
        svc.borrow_book('U101', 'B001')
        svc.return_book('U101', 'B001')
        assert db.users['U101'].active_loans == 0

    def test_return_loan_status_becomes_returned(self, svc):
        r = svc.borrow_book('U101', 'B001')
        loan_id = r['loan']['loan_id']
        svc.return_book('U101', 'B001')
        assert db.loans[loan_id]['status'] == 'RETURNED'

    def test_return_without_borrow(self, svc):
        result = svc.return_book('U101', 'B001')
        assert result['success'] is False
        assert result['code'] == 404

    def test_return_nonexistent_user(self, svc):
        result = svc.return_book('U999', 'B001')
        assert result['success'] is False
        assert result['code'] == 404

    def test_return_nonexistent_book(self, svc):
        result = svc.return_book('U101', 'B999')
        assert result['success'] is False
        assert result['code'] == 404

    def test_double_return_rejected(self, svc):
        svc.borrow_book('U101', 'B001')
        svc.return_book('U101', 'B001')
        result = svc.return_book('U101', 'B001')
        assert result['success'] is False
        assert result['code'] == 404

    def test_return_timestamps_set(self, svc):
        svc.borrow_book('U101', 'B001')
        result = svc.return_book('U101', 'B001')
        loan = result['loan']
        assert loan['borrowed_at'] is not None
        assert loan['returned_at'] is not None
        # returned_at must be >= borrowed_at
        from datetime import datetime
        bt = datetime.fromisoformat(loan['borrowed_at'])
        rt = datetime.fromisoformat(loan['returned_at'])
        assert rt >= bt
