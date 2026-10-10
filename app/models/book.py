from dataclasses import dataclass


@dataclass
class Book:
    """Book model representing a library book."""
    book_id: str
    title: str
    author: str
    isbn: str
    total_copies: int
    available_copies: int

    def to_dict(self) -> dict:
        return {
            'book_id': self.book_id,
            'title': self.title,
            'author': self.author,
            'isbn': self.isbn,
            'total_copies': self.total_copies,
            'available_copies': self.available_copies,
            'status': 'Available' if self.available_copies > 0 else 'Out of Stock',
        }

    @staticmethod
    def from_dict(data: dict) -> 'Book':
        total = int(data.get('total_copies', 1))
        available = int(data.get('available_copies', total))
        return Book(
            book_id=data['book_id'],
            title=data['title'],
            author=data['author'],
            isbn=data['isbn'],
            total_copies=total,
            available_copies=available,
        )

    @property
    def is_available(self) -> bool:
        return self.available_copies > 0
