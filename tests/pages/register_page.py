"""Register Page Object."""
import logging

from playwright.sync_api import Page, expect

from src.utils.stability import handle_internal_error, safe_click

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
        self.register_button.wait_for(state="visible", timeout=10000)
        safe_click(self.register_button)
        # ParaBank registration can be very slow, wait for network
        self.page.wait_for_load_state("networkidle", timeout=15000)

    def verify_registration_success(self, username: str, password: str = "password123") -> None:
        """Verify that registration was successful with robust error checking and fallback.

        ParaBank has a bug where it reports 'username already exists' even for successful creations.
        This method handles that by attempting a login check if the welcome message is missing.
        """
        # First check for internal errors
        handle_internal_error(self.page, requires_login=False)

        try:
            # Attempt to find the success message
            expect(self.success_message).to_contain_text(f"Welcome {username}", timeout=10000)
            expect(self.page.locator("#rightPanel p")).to_contain_text(
                "Your account was created successfully. You are now logged in.", timeout=5000
            )
            logger.info("Registration successful (Success message detected).")
        except AssertionError as e:
            # If success message is missing, check if it's the known "already exists" bug
            error_locator = self.page.locator("span[id='customer\\.username\\.errors']")
            if (
                error_locator.is_visible(timeout=2000)
                and "already exists" in error_locator.inner_text().lower()
            ):
                logger.warning(
                    f"Detected potential false-positive duplicate error for {username}. "
                    "Verifying via login..."
                )

                # Try to log in from the login panel on the current page
                from tests.pages.home_login_page import (  # pylint: disable=import-outside-toplevel
                    HomePage,
                )

                home_page = HomePage(self.page)
                # Use assert_success=False to handle the logic manually
                home_page.user_log_in(username, password, assert_success=False)

                # If we are now on the overview page, it means registration actually worked
                import re  # pylint: disable=import-outside-toplevel

                if re.search(r".*/overview\.htm$", self.page.url):
                    logger.info(
                        "Registration verified via successful login (ParaBank UI bug bypassed)."
                    )
                    return

            # If login failed or it wasn't the expected error, raise the original exception
            logger.error(f"Registration failed: {str(e)}")
            raise e
