"""Update Contact Info Page Object."""
import logging

from playwright.sync_api import Page, expect

logger = logging.getLogger("parabank")


class UpdateContactInfoPage:
    """Update Contact Info Page Object."""

    def __init__(self, page: Page) -> None:
        self.page = page
        self.first_name_input = page.locator("[id='customer.firstName']")
        self.last_name_input = page.locator("[id='customer.lastName']")
        self.address_input = page.locator("[id='customer.address.street']")
        self.city_input = page.locator("[id='customer.address.city']")
        self.state_input = page.locator("[id='customer.address.state']")
        self.zip_code_input = page.locator("[id='customer.address.zipCode']")
        self.phone_input = page.locator("[id='customer.phoneNumber']")
        self.update_button = page.locator("input[value='Update Profile']")

    def wait_for_data(self) -> None:
        """Wait for the form to be populated with data."""
        # Wait for first name to have a value (it should be pre-filled)
        expect(self.first_name_input).not_to_have_value("", timeout=10000)
        logger.info("Form data loaded.")

    def update_phone_number(self, new_phone: str) -> None:
        """Update just the phone number."""
        self.wait_for_data()
        logger.info(f"Updating phone number to {new_phone}")
        self.phone_input.fill(new_phone)
        self.update_button.click()

    def update_zip_code(self, new_zip: str) -> None:
        """Update just the zip code."""
        self.wait_for_data()
        logger.info(f"Updating zip code to {new_zip}")
        self.zip_code_input.fill(new_zip)
        self.update_button.click()

    def get_success_text(self) -> str:
        """Get the success message text."""
        success_header = self.page.locator("#rightPanel").get_by_text("Profile Updated").first
        expect(success_header).to_be_visible()
        return str(success_header.inner_text())
