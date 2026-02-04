import uuid

from faker import Faker

from tests.data.models import User


class UserFactory:
    """Factory for generating realistic test user data."""

    def __init__(self, locale: str = "en_US"):
        self.fake = Faker(locale)

    def create_user(self, username_prefix: str = "user") -> User:
        """Create a randomized User object.

        Args:
            username_prefix: Prefix for the generated username to avoid collisions.

        Returns:
            User: A populated User object with randomized data.
        """
        # Ensure unique username even with Faker's randomness
        unique_suffix = uuid.uuid4().hex[:8]
        username = f"{username_prefix}_{unique_suffix}"

        return User(
            first_name=self.fake.first_name(),
            last_name=self.fake.last_name(),
            address=self.fake.street_address(),
            city=self.fake.city(),
            state=self.fake.state_abbr(),
            zip_code=self.fake.zipcode(),
            phone=self.fake.phone_number(),
            ssn=self.fake.ssn(),
            username=username,
            password="Password123!",  # Static or randomized, but usually static is fine for testing
        )
