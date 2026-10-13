from datetime import datetime, timezone, timedelta
from database.db import db
from app.models.user import User
from app.models.book import Book


class LibraryService:
    """Core business logic for the library management system."""

    VALID_ROLES = {'Student', 'Faculty'}

    # ─────────────────────────── USER OPERATIONS ────────────────────────────

    def add_user(self, data: dict) -> dict:
        """Create a new library user."""
        user_id = (data.get('user_id') or '').strip()
        name = (data.get('name') or '').strip()
        email = (data.get('email') or '').strip()
        role = (data.get('role') or '').strip()

        if not user_id:
            return {'success': False, 'error': 'user_id is required', 'code': 400}
        if not name:
            return {'success': False, 'error': 'name is required', 'code': 400}
        if not email:
            return {'success': False, 'error': 'email is required', 'code': 400}
        if role not in self.VALID_ROLES:
            return {
                'success': False,
                'error': f"role must be one of: {', '.join(self.VALID_ROLES)}",
                'code': 400,
            }

        with db.get_data_lock():
            if user_id in db.users:
                return {
                    'success': False,
                    'error': f"User with ID '{user_id}' already exists",
                    'code': 409,
                }
            user = User(
                user_id=user_id,
                name=name,
                email=email,
                role=role,
                active_loans=0,
            )
            db.users[user_id] = user
            return {'success': True, 'user': user.to_dict(), 'code': 201}

    def get_user(self, user_id: str) -> dict:
        """Retrieve a user by ID."""
        with db.get_data_lock():
            user = db.users.get(user_id)
            if not user:
                return {
                    'success': False,
                    'error': f"User '{user_id}' not found",
                    'code': 404,
                }
            return {'success': True, 'user': user.to_dict(), 'code': 200}

    def get_all_users(self) -> dict:
        """Return all users."""
        with db.get_data_lock():
            return {
                'success': True,
                'users': [u.to_dict() for u in db.users.values()],
                'code': 200,
            }

    def delete_user(self, user_id: str) -> dict:
        """Delete a user only when they have no active loans."""
        with db.get_data_lock():
            user = db.users.get(user_id)
            if not user:
                return {
                    'success': False,
                    'error': f"User '{user_id}' not found",
                    'code': 404,
                }
            if user.active_loans > 0:
                return {
                    'success': False,
                    'error': (
                        f"Cannot delete user '{user_id}': "
                        f"user has {user.active_loans} active loan(s)"
                    ),
                    'code': 409,
                }
            del db.users[user_id]
            return {'success': True, 'message': f"User '{user_id}' deleted", 'code': 200}

    def update_user(self, user_id: str, data: dict) -> dict:
        """Update existing user profile (name, email, role)."""
        with db.get_data_lock():
            user = db.users.get(user_id)
            if not user:
                return {'success': False, 'error': f"User '{user_id}' not found", 'code': 404}

            if 'name' in data:
                name = (data.get('name') or '').strip()
                if not name:
                    return {'success': False, 'error': 'name cannot be empty', 'code': 400}
                user.name = name

            if 'email' in data:
                email = (data.get('email') or '').strip()
                if not email:
                    return {'success': False, 'error': 'email cannot be empty', 'code': 400}
                user.email = email

            if 'role' in data:
                role = (data.get('role') or '').strip()
                if role not in self.VALID_ROLES:
                    return {
                        'success': False,
                        'error': f"role must be one of: {', '.join(self.VALID_ROLES)}",
                        'code': 400,
                    }
                if role == 'Student' and user.active_loans > 3:
                    return {
                        'success': False,
                        'error': (
                            f"Cannot change role to Student: user currently has "
                            f"{user.active_loans} active loans (Student limit is 3)"
                        ),
                        'code': 409,
                    }
                user.role = role

            return {'success': True, 'user': user.to_dict(), 'code': 200}

    def get_user_loans(self, user_id: str) -> dict:
        """Get all loans associated with a specific user."""
        with db.get_data_lock():
            if user_id not in db.users:
                return {'success': False, 'error': f"User '{user_id}' not found", 'code': 404}
            user_loans = [
                ln for ln in db.loans.values()
                if ln['user_id'] == user_id
            ]
            return {'success': True, 'user_id': user_id, 'loans': user_loans, 'code': 200}

    # ─────────────────────────── BOOK OPERATIONS ────────────────────────────

    def add_book(self, data: dict) -> dict:
        """Add a new book to the catalog."""
        book_id = (data.get('book_id') or '').strip()
        title = (data.get('title') or '').strip()
        author = (data.get('author') or '').strip()
        isbn = (data.get('isbn') or '').strip()

        if not book_id:
            return {'success': False, 'error': 'book_id is required', 'code': 400}
        if not title:
            return {'success': False, 'error': 'title is required', 'code': 400}
        if not author:
            return {'success': False, 'error': 'author is required', 'code': 400}
        if not isbn:
            return {'success': False, 'error': 'isbn is required', 'code': 400}

        try:
            total_copies = int(data.get('total_copies', 1))
        except (TypeError, ValueError):
            return {'success': False, 'error': 'total_copies must be an integer', 'code': 400}

        if total_copies < 1:
            return {
                'success': False,
                'error': 'total_copies must be at least 1',
                'code': 400,
            }

        with db.get_data_lock():
            if book_id in db.books:
                return {
                    'success': False,
                    'error': f"Book with ID '{book_id}' already exists",
                    'code': 409,
                }
            book = Book(
                book_id=book_id,
                title=title,
                author=author,
                isbn=isbn,
                total_copies=total_copies,
                available_copies=total_copies,
            )
            db.books[book_id] = book
            return {'success': True, 'book': book.to_dict(), 'code': 201}

    def get_book(self, book_id: str) -> dict:
        """Retrieve a book by ID."""
        with db.get_data_lock():
            book = db.books.get(book_id)
            if not book:
                return {
                    'success': False,
                    'error': f"Book '{book_id}' not found",
                    'code': 404,
                }
            return {'success': True, 'book': book.to_dict(), 'code': 200}

    def search_books(self, query: str = '') -> dict:
        """Search books by title, author, or ISBN (case-insensitive)."""
        q = (query or '').strip().lower()
        with db.get_data_lock():
            if not q:
                books = [b.to_dict() for b in db.books.values()]
            else:
                books = [
                    b.to_dict()
                    for b in db.books.values()
                    if q in b.title.lower()
                    or q in b.author.lower()
                    or q in b.isbn.lower()
                ]
            return {'success': True, 'books': books, 'code': 200}

    def update_book(self, book_id: str, data: dict) -> dict:
        """Update existing book details (title, author, isbn, total_copies)."""
        with db.get_data_lock():
            book = db.books.get(book_id)
            if not book:
                return {'success': False, 'error': f"Book '{book_id}' not found", 'code': 404}

            if 'title' in data:
                new_title = (data.get('title') or '').strip()
                if not new_title:
                    return {'success': False, 'error': 'title cannot be empty', 'code': 400}
                book.title = new_title

            if 'author' in data:
                new_author = (data.get('author') or '').strip()
                if not new_author:
                    return {'success': False, 'error': 'author cannot be empty', 'code': 400}
                book.author = new_author

            if 'isbn' in data:
                new_isbn = (data.get('isbn') or '').strip()
                if not new_isbn:
                    return {'success': False, 'error': 'isbn cannot be empty', 'code': 400}
                book.isbn = new_isbn

            if 'total_copies' in data:
                try:
                    new_total = int(data['total_copies'])
                except (TypeError, ValueError):
                    return {'success': False, 'error': 'total_copies must be an integer', 'code': 400}

                borrowed_copies = book.total_copies - book.available_copies
                if new_total < borrowed_copies:
                    return {
                        'success': False,
                        'error': (
                            f"total_copies ({new_total}) cannot be less than "
                            f"active borrowed copies ({borrowed_copies})"
                        ),
                        'code': 400,
                    }
                if new_total < 1:
                    return {'success': False, 'error': 'total_copies must be at least 1', 'code': 400}

                diff = new_total - book.total_copies
                book.total_copies = new_total
                book.available_copies += diff

            return {'success': True, 'book': book.to_dict(), 'code': 200}

    def delete_book(self, book_id: str) -> dict:
        """Delete a book from catalog only if no copies are actively borrowed."""
        with db.get_data_lock():
            book = db.books.get(book_id)
            if not book:
                return {'success': False, 'error': f"Book '{book_id}' not found", 'code': 404}

            active_loans = sum(
                1 for ln in db.loans.values()
                if ln['book_id'] == book_id and ln['status'] == 'ACTIVE'
            )
            if active_loans > 0:
                return {
                    'success': False,
                    'error': (
                        f"Cannot delete book '{book_id}': "
                        f"{active_loans} copy/copies currently on active loan"
                    ),
                    'code': 409,
                }

            del db.books[book_id]
            return {'success': True, 'message': f"Book '{book_id}' deleted successfully", 'code': 200}

    def get_all_loans(self) -> dict:
        """Return all loan records."""
        with db.get_data_lock():
            return {
                'success': True,
                'loans': list(db.loans.values()),
                'code': 200,
            }

    # ─────────────────────── BORROW / RETURN OPERATIONS ─────────────────────

    def borrow_book(self, user_id: str, book_id: str) -> dict:
        """Process a book borrowing transaction."""
        with db.get_data_lock():
            user = db.users.get(user_id)
            if not user:
                return {
                    'success': False,
                    'error': f"User '{user_id}' not found",
                    'code': 404,
                }

            book = db.books.get(book_id)
            if not book:
                return {
                    'success': False,
                    'error': f"Book '{book_id}' not found",
                    'code': 404,
                }

            if user.loan_limit_reached:
                return {
                    'success': False,
                    'error': (
                        f"{user.role} '{user.name}' has reached the maximum "
                        f"loan limit of {user.max_loans}"
                    ),
                    'code': 409,
                }

            if not book.is_available:
                return {
                    'success': False,
                    'error': 'Book is currently out of stock',
                    'code': 409,
                }

            # All checks passed — create the loan
            loan_id = db.next_loan_id()
            now = datetime.now(timezone.utc)
            loan_period_days = 30 if user.role == 'Faculty' else 14
            due_at = (now + timedelta(days=loan_period_days)).isoformat()

            loan = {
                'loan_id': loan_id,
                'user_id': user_id,
                'book_id': book_id,
                'borrowed_at': now.isoformat(),
                'due_at': due_at,
                'renewal_count': 0,
                'returned_at': None,
                'status': 'ACTIVE',
            }
            db.loans[loan_id] = loan
            book.available_copies -= 1
            user.active_loans += 1

            return {'success': True, 'loan': loan, 'code': 201}

    def return_book(self, user_id: str, book_id: str) -> dict:
        """Process a book return transaction."""
        with db.get_data_lock():
            user = db.users.get(user_id)
            if not user:
                return {
                    'success': False,
                    'error': f"User '{user_id}' not found",
                    'code': 404,
                }

            book = db.books.get(book_id)
            if not book:
                return {
                    'success': False,
                    'error': f"Book '{book_id}' not found",
                    'code': 404,
                }

            # Find matching ACTIVE loan
            active_loan = None
            for loan in db.loans.values():
                if (
                    loan['user_id'] == user_id
                    and loan['book_id'] == book_id
                    and loan['status'] == 'ACTIVE'
                ):
                    active_loan = loan
                    break

            if not active_loan:
                return {
                    'success': False,
                    'error': (
                        f"No active loan found for user '{user_id}' "
                        f"and book '{book_id}'"
                    ),
                    'code': 404,
                }

            # Process the return
            active_loan['status'] = 'RETURNED'
            active_loan['returned_at'] = datetime.now(timezone.utc).isoformat()
            book.available_copies += 1
            user.active_loans = max(0, user.active_loans - 1)

            return {'success': True, 'loan': active_loan, 'code': 200}

    def renew_loan(self, loan_id: str) -> dict:
        """Renew an active loan, extending its due date (max 2 renewals)."""
        with db.get_data_lock():
            loan = db.loans.get(loan_id)
            if not loan:
                return {'success': False, 'error': f"Loan '{loan_id}' not found", 'code': 404}

            if loan.get('status') != 'ACTIVE':
                return {
                    'success': False,
                    'error': f"Cannot renew loan '{loan_id}': loan is {loan.get('status')}",
                    'code': 400,
                }

            if loan.get('renewal_count', 0) >= 2:
                return {
                    'success': False,
                    'error': f"Loan '{loan_id}' has reached maximum renewal limit of 2",
                    'code': 409,
                }

            user = db.users.get(loan['user_id'])
            extension_days = 30 if (user and user.role == 'Faculty') else 14

            current_due = loan.get('due_at')
            if current_due:
                try:
                    dt = datetime.fromisoformat(current_due)
                    new_due = (dt + timedelta(days=extension_days)).isoformat()
                except Exception:
                    new_due = (datetime.now(timezone.utc) + timedelta(days=extension_days)).isoformat()
            else:
                new_due = (datetime.now(timezone.utc) + timedelta(days=extension_days)).isoformat()

            loan['renewal_count'] = loan.get('renewal_count', 0) + 1
            loan['due_at'] = new_due

            return {
                'success': True,
                'message': f"Loan '{loan_id}' renewed successfully",
                'loan': loan,
                'code': 200,
            }

    def get_dashboard_stats(self) -> dict:
        """Aggregate statistics for the dashboard."""
        with db.get_data_lock():
            total_books = len(db.books)
            total_copies = sum(b.total_copies for b in db.books.values())
            available_copies = sum(b.available_copies for b in db.books.values())
            total_users = len(db.users)
            active_loans = sum(
                1 for ln in db.loans.values() if ln['status'] == 'ACTIVE'
            )
            returned_loans = sum(
                1 for ln in db.loans.values() if ln['status'] == 'RETURNED'
            )
            return {
                'total_books': total_books,
                'total_copies': total_copies,
                'available_copies': available_copies,
                'total_users': total_users,
                'active_loans': active_loans,
                'returned_loans': returned_loans,
            }

    def export_system_data(self) -> dict:
        """Export comprehensive system snapshot for backup and auditing."""
        with db.get_data_lock():
            return {
                'success': True,
                'version': '1.0.0',
                'exported_at': datetime.now(timezone.utc).isoformat(),
                'users': [u.to_dict() for u in db.users.values()],
                'books': [b.to_dict() for b in db.books.values()],
                'loans': list(db.loans.values()),
                'stats': {
                    'total_books': len(db.books),
                    'total_users': len(db.users),
                    'total_loans': len(db.loans),
                },
                'code': 200,
            }


# Module-level service instance
library_service = LibraryService()
