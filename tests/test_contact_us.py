"""Tests for Customer Care Contact Us."""
from playwright.sync_api import Page, expect

from tests.pages.contact_us_page import ContactUsPage
from tests.pages.home_login_page import HomePage


def test_contact_us_submission(page: Page, base_url: str) -> None:
    """Test submitting the Contact Us form successfully."""
    home_page = HomePage(page)
    home_page.load(base_url)

    # Click contact link
    home_page.contact_link.click()

    contact_page = ContactUsPage(page)
    contact_page.submit_contact_form(
        name="Test User",
        email="test@example.com",
        phone="1234567890",
        message="This is a test message for customer care.",
    )

    contact_page.verify_submission_success()


def test_contact_us_validation(page: Page, base_url: str) -> None:
    """Test validation errors on the Contact Us form."""
    home_page = HomePage(page)
    home_page.load(base_url)
    home_page.contact_link.click()

    contact_page = ContactUsPage(page)
    contact_page.submit_button.click()

    # Expected: "Name is required.", "Email is required.", etc.
    expect(page.locator("span[id='name.errors']")).to_be_visible(timeout=10000)
    expect(page.locator("span[id='email.errors']")).to_be_visible(timeout=10000)
    expect(page.locator("span[id='phone.errors']")).to_be_visible(timeout=10000)
    expect(page.locator("span[id='message.errors']")).to_be_visible(timeout=10000)


def test_contact_us_elements_visibility(page: Page, base_url: str) -> None:
    """Verify that all elements of the Contact Us page are visible."""
    home_page = HomePage(page)
    home_page.load(base_url)
    home_page.contact_link.click()

    contact_page = ContactUsPage(page)
    expect(contact_page.name_input).to_be_visible()
    expect(contact_page.email_input).to_be_visible()
    expect(contact_page.phone_input).to_be_visible()
    expect(contact_page.message_textarea).to_be_visible()
    expect(contact_page.submit_button).to_be_visible()
