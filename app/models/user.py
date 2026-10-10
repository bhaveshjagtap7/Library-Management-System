from dataclasses import dataclass


@dataclass
class User:
    """User model representing a library member."""
    user_id: str
    name: str
    email: str
    role: str  # 'Student' or 'Faculty'
    active_loans: int = 0

    def to_dict(self) -> dict:
        return {
            'user_id': self.user_id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'active_loans': self.active_loans,
        }

    @staticmethod
    def from_dict(data: dict) -> 'User':
        return User(
            user_id=data['user_id'],
            name=data['name'],
            email=data['email'],
            role=data['role'],
            active_loans=data.get('active_loans', 0),
        )

    @property
    def max_loans(self) -> int:
        """Return maximum allowed active loans based on role."""
        return 5 if self.role == 'Faculty' else 3

    @property
    def loan_limit_reached(self) -> bool:
        return self.active_loans >= self.max_loans
