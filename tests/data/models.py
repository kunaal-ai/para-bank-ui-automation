from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class User:
    """Represents a user in the ParaBank system."""

    first_name: str
    last_name: str
    address: str
    city: str
    state: str
    zip_code: str
    phone: str
    ssn: str
    username: str
    password: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert the user object to a dictionary for form filling."""
        return {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "address": self.address,
            "city": self.city,
            "state": self.state,
            "zip_code": self.zip_code,
            "phone": self.phone,
            "ssn": self.ssn,
            "username": self.username,
            "password": self.password,
        }
