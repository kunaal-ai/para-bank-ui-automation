import uuid

from playwright.sync_api import Page, expect

from tests.pages.home_login_page import HomePage
from tests.pages.register_page import RegisterPage


def test_register_new_user(page: Page, base_url: str) -> None:
    """Test registering a new user successfully."""
    home_page = HomePage(page)
    home_page.load(base_url)

    # Click register link
    page.get_by_role("link", name="Register").click()

    register_page = RegisterPage(page)

    # Generate unique username using UUID
    username = f"user_{uuid.uuid4().hex[:12]}"

    user_data = {
        "first_name": "Test",
        "last_name": "User",
        "address": "123 Main St",
        "city": "Beverly Hills",
        "state": "CA",
        "zip_code": "90210",
        "phone": "555-0199",
        "ssn": "000-00-0000",
        "username": username,
        "password": "password123",
    }

    register_page.register(user_data)
    register_page.verify_registration_success(username, user_data["password"])


def test_registration_validation_errors(page: Page, base_url: str) -> None:
    """Test registration validation errors when fields are missing."""
    home_page = HomePage(page)
    home_page.load(base_url)

    # Click register link
    page.get_by_role("link", name="Register").click()

    register_page = RegisterPage(page)

    # Click register without filling anything
    register_page.register_button.click()

    # Check for error messages
    expect(page.locator("span[id='customer\\.firstName\\.errors']")).to_be_visible()
    expect(page.locator("span[id='customer\\.lastName\\.errors']")).to_be_visible()
    expect(page.locator("span[id='customer\\.username\\.errors']")).to_be_visible()


def test_registration_duplicate_username(page: Page, base_url: str) -> None:
    """Test registration with an already existing username."""
    home_page = HomePage(page)
    home_page.load(base_url)
    page.get_by_role("link", name="Register").click()
    register_page = RegisterPage(page)

    # First registration with unique username
    username = f"dup_{uuid.uuid4().hex[:12]}"
    user_data = {
        "first_name": "Dup",
        "last_name": "User",
        "username": username,
        "password": "password123",
    }
    register_page.register(user_data)
    register_page.verify_registration_success(username, user_data["password"])

    # Logout to try registering again with same username
    page.get_by_role("link", name="Log Out").click()
    page.get_by_role("link", name="Register").click()

    # Second registration with same username
    register_page.register(user_data)
    expect(page.locator("span[id='customer\\.username\\.errors']")).to_have_text(
        "This username already exists."
    )


def test_registration_password_mismatch(page: Page, base_url: str) -> None:
    """Test registration when password and confirmation password do not match."""
    home_page = HomePage(page)
    home_page.load(base_url)
    page.get_by_role("link", name="Register").click()
    register_page = RegisterPage(page)

    register_page.first_name_input.fill("Mismatch")
    register_page.last_name_input.fill("User")
    # Generate unique mismatch_user using UUID
    username = f"mismatch_{uuid.uuid4().hex[:12]}"

    register_page.first_name_input.fill("Mismatch")
    register_page.last_name_input.fill("User")
    register_page.username_input.fill(username)
    register_page.password_input.fill("password123")
    register_page.confirm_password_input.fill("different_password")
    register_page.register_button.click()

    expect(page.locator("span[id='repeatedPassword\\.errors']")).to_have_text(
        "Passwords did not match."
    )
