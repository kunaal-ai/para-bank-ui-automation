"""Page Object Model for the Forgot Login (Customer Lookup) page."""

from playwright.sync_api import Locator, Page


class ForgotLoginPage:
    """Page object for the Customer Lookup (Forgot Login) page."""

    def __init__(self, page: Page) -> None:
        """Initialize the Forgot Login page object.

        Args:
            page: Playwright page instance
        """
        self.page = page

        # Form fields
        self.first_name_input: Locator = page.locator("#firstName")
        self.last_name_input: Locator = page.locator("#lastName")
        self.address_input: Locator = page.locator("#address\\.street")
        self.city_input: Locator = page.locator("#address\\.city")
        self.state_input: Locator = page.locator("#address\\.state")
        self.zip_code_input: Locator = page.locator("#address\\.zipCode")
        self.ssn_input: Locator = page.locator("#ssn")

        # Submit button
        # Submit button - using has-text or regex to be case-insensitive
        self.find_login_button: Locator = page.locator('input.button[value="Find My Login Info"]')

        # Result elements
        self.success_message: Locator = page.locator("p.smallText").filter(
            has_text="Your login information was located successfully"
        )
        self.error_message: Locator = page.locator("p.error")

        # Validation error messages
        self.first_name_error: Locator = page.locator("#firstName\\.errors")
        self.last_name_error: Locator = page.locator("#lastName\\.errors")
        self.address_error: Locator = page.locator("#address\\.street\\.errors")
        self.city_error: Locator = page.locator("#address\\.city\\.errors")
        self.state_error: Locator = page.locator("#address\\.state\\.errors")
        self.zip_code_error: Locator = page.locator("#address\\.zipCode\\.errors")
        self.ssn_error: Locator = page.locator("#ssn\\.errors")

        # Page elements
        self.page_title: Locator = page.locator("h1.title")
        # Use more specific locator for the instruction paragraph
        self.instruction_text: Locator = page.locator(
            "#rightPanel >> p:text('Please fill out the following information')"
        )

    def navigate(self, base_url: str) -> None:
        """Navigate to the Forgot Login page.

        Args:
            base_url: Base URL of the application
        """
        self.page.goto(f"{base_url}/lookup.htm")

    def fill_lookup_form(
        self,
        first_name: str,
        last_name: str,
        address: str,
        city: str,
        state: str,
        zip_code: str,
        ssn: str,
    ) -> None:
        """Fill out the customer lookup form.

        Args:
            first_name: Customer first name
            last_name: Customer last name
            address: Street address
            city: City
            state: State
            zip_code: Zip code
            ssn: Social security number
        """
        self.first_name_input.fill(first_name)
        self.last_name_input.fill(last_name)
        self.address_input.fill(address)
        self.city_input.fill(city)
        self.state_input.fill(state)
        self.zip_code_input.fill(zip_code)
        self.ssn_input.fill(ssn)

    def submit_lookup(self) -> None:
        """Submit the customer lookup form."""
        self.find_login_button.click()

    def lookup_customer(
        self,
        first_name: str,
        last_name: str,
        address: str,
        city: str,
        state: str,
        zip_code: str,
        ssn: str,
    ) -> None:
        """Complete customer lookup flow.

        Args:
            first_name: Customer first name
            last_name: Customer last name
            address: Street address
            city: City
            state: State
            zip_code: Zip code
            ssn: Social security number
        """
        self.fill_lookup_form(first_name, last_name, address, city, state, zip_code, ssn)
        self.submit_lookup()
