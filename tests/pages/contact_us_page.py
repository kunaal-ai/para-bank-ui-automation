"""Contact Us Page Object."""
import logging

from playwright.sync_api import Page, expect

logger = logging.getLogger("parabank")


class ContactUsPage:
    """Contact Us Page Object."""

    def __init__(self, page: Page) -> None:
        self.page = page
        self.name_input = page.locator('input[id="name"]')
        self.email_input = page.locator('input[id="email"]')
        self.phone_input = page.locator('input[id="phone"]')
        self.message_textarea = page.locator('textarea[id="message"]')
        self.submit_button = page.locator('input[value="Send to Customer Care"]')
        self.success_title = page.locator("#rightPanel h1.title")
        self.success_message = page.locator("#rightPanel p").first

    def submit_contact_form(self, name: str, email: str, phone: str, message: str) -> None:
        """Fill and submit the contact form."""
        logger.info(f"Submitting contact form for {name}")
        self.name_input.fill(name)
        self.email_input.fill(email)
        self.phone_input.fill(phone)
        self.message_textarea.fill(message)
        self.submit_button.click()

    def verify_submission_success(self) -> None:
        """Verify that the contact form was submitted successfully."""
        expect(self.success_title).to_have_text("Customer Care")
        expect(self.success_message).to_contain_text("Thank you")
        logger.info("Contact form submitted successfully.")
