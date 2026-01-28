"""Register Page Object."""
import logging

from playwright.sync_api import Page, expect

logger = logging.getLogger("parabank")


class RegisterPage:
    """Register Page Object."""

    def __init__(self, page: Page) -> None:
        self.page = page
        self.first_name_input = page.locator('input[id="customer\\.firstName"]')
        self.last_name_input = page.locator('input[id="customer\\.lastName"]')
        self.address_input = page.locator('input[id="customer\\.address\\.street"]')
        self.city_input = page.locator('input[id="customer\\.address\\.city"]')
        self.state_input = page.locator('input[id="customer\\.address\\.state"]')
        self.zip_code_input = page.locator('input[id="customer\\.address\\.zipCode"]')
        self.phone_input = page.locator('input[id="customer\\.phoneNumber"]')
        self.ssn_input = page.locator('input[id="customer\\.ssn"]')
        self.username_input = page.locator('input[id="customer\\.username"]')
        self.password_input = page.locator('input[id="customer\\.password"]')
        self.confirm_password_input = page.locator('input[id="repeatedPassword"]')
        self.register_button = page.locator('input[value="Register"]')
        self.success_message = page.locator("#rightPanel .title")
        self.error_message = page.locator(".error")

    def register(self, user_data: dict) -> None:
        """Fill the registration form and submit."""
        logger.info(f"Registering user: {user_data.get('username')}")
        self.first_name_input.fill(user_data.get("first_name", "Test"))
        self.last_name_input.fill(user_data.get("last_name", "User"))
        self.address_input.fill(user_data.get("address", "123 Street"))
        self.city_input.fill(user_data.get("city", "City"))
        self.state_input.fill(user_data.get("state", "State"))
        self.zip_code_input.fill(user_data.get("zip_code", "12345"))
        self.phone_input.fill(user_data.get("phone", "1234567890"))
        self.ssn_input.fill(user_data.get("ssn", "123-456-789"))
        self.username_input.fill(user_data.get("username"))
        self.password_input.fill(user_data.get("password"))
        self.confirm_password_input.fill(user_data.get("password"))
        self.register_button.click()

    def verify_registration_success(self, username: str) -> None:
        """Verify that registration was successful."""
        expect(self.success_message).to_contain_text(f"Welcome {username}")
        expect(self.page.locator("#rightPanel p")).to_contain_text(
            "Your account was created successfully. You are now logged in."
        )
        logger.info("Registration successful.")
