import threading
from app.models.user import User
from app.models.book import Book


class Database:
    """Thread-safe singleton in-memory database."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._data_lock = threading.RLock()
        self.users = {}
        self.books = {}
        self.loans = {}
        self._loan_counter = 0
        self._seed_data()
        self._initialized = True

    def _seed_data(self):
        """Seed initial users and books."""
        initial_users = [
            User(
                user_id='U101',
                name='Alice Johnson',
                email='alice@university.edu',
                role='Student',
                active_loans=0,
            ),
            User(
                user_id='U102',
                name='Dr. Robert Smith',
                email='robert.smith@university.edu',
                role='Faculty',
                active_loans=0,
            ),
        ]
        for user in initial_users:
            self.users[user.user_id] = user

        initial_books = [
            Book(
                book_id='B001',
                title='Cloud Native DevOps Architecture',
                author='Linus Torvalds',
                isbn='978-0134685991',
                total_copies=5,
                available_copies=5,
            ),
            Book(
                book_id='B002',
                title='Continuous Delivery Principles',
                author='Jez Humble & David Farley',
                isbn='978-0321601919',
                total_copies=3,
                available_copies=3,
            ),
        ]
        for book in initial_books:
            self.books[book.book_id] = book

    def reset(self):
        """Reset database to initial seeded state (for testing)."""
        with self._data_lock:
            self.users = {}
            self.books = {}
            self.loans = {}
            self._loan_counter = 0
            self._seed_data()

    def next_loan_id(self) -> str:
        """Generate the next sequential loan ID."""
        with self._data_lock:
            self._loan_counter += 1
            return f'L-{self._loan_counter:04d}'

    def get_data_lock(self):
        return self._data_lock


# Module-level singleton instance
db = Database()
