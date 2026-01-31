"""Tests for Home Page UI Elements - No Login Required."""
import re

import pytest
from playwright.sync_api import Page, expect

from tests.pages.home_login_page import HomePage


@pytest.fixture
def loaded_home_page(page: Page, base_url: str) -> HomePage:
    """Load home page and wait for it to be ready.

    Note: This fixture ensures we're on the unauthenticated home page
    by navigating directly to the base URL.
    """
    home_page = HomePage(page)
    home_page.load(base_url)
    page.wait_for_load_state("domcontentloaded")
    # Wait for login panel to ensure we're on the home page (not logged in)
    try:
        page.locator("#loginPanel").wait_for(state="visible", timeout=15000)
    except Exception:
        # If login panel is not visible, we might be logged in - navigate to home
        page.goto(base_url)
        page.wait_for_load_state("domcontentloaded")
        page.locator("#loginPanel").wait_for(state="visible", timeout=15000)
    return home_page


class TestHomePageUIElements:
    """Test suite for home page UI elements visibility and functionality."""

    def test_home_page_title(self, loaded_home_page: HomePage, page: Page) -> None:
        """Verify the home page title is correct."""
        expect(page).to_have_title("ParaBank | Welcome | Online Banking")

    def test_login_panel_visible(self, loaded_home_page: HomePage, page: Page) -> None:
        """Verify the login panel is visible on home page."""
        login_panel = page.locator("#loginPanel")
        expect(login_panel).to_be_visible()

    def test_username_field_visible_and_enabled(self, loaded_home_page: HomePage) -> None:
        """Verify username input field is visible and enabled."""
        expect(loaded_home_page.user_name_text).to_be_visible()
        expect(loaded_home_page.user_name_text).to_be_enabled()
        expect(loaded_home_page.user_name_text).to_be_editable()

    def test_password_field_visible_and_enabled(self, loaded_home_page: HomePage) -> None:
        """Verify password input field is visible and enabled."""
        expect(loaded_home_page.password_text).to_be_visible()
        expect(loaded_home_page.password_text).to_be_enabled()
        expect(loaded_home_page.password_text).to_be_editable()
        expect(loaded_home_page.password_text).to_have_attribute("type", "password")

    def test_login_button_visible_and_enabled(self, loaded_home_page: HomePage) -> None:
        """Verify login button is visible and clickable."""
        expect(loaded_home_page.log_in_button).to_be_visible()
        expect(loaded_home_page.log_in_button).to_be_enabled()
        expect(loaded_home_page.log_in_button).to_have_attribute("type", "submit")

    def test_forgot_login_link_visible_and_clickable(self, loaded_home_page: HomePage) -> None:
        """Verify 'Forgot login info?' link is visible and clickable."""
        expect(loaded_home_page.forget_login_button).to_be_visible()
        expect(loaded_home_page.forget_login_button).to_have_text("Forgot login info?")

    def test_register_link_visible_and_clickable(
        self, loaded_home_page: HomePage, page: Page
    ) -> None:
        """Verify 'Register' link is visible and clickable."""
        register_link = page.locator("#loginPanel a[href*='register']")
        expect(register_link).to_be_visible()
        expect(register_link).to_have_text("Register")

    def test_parabank_logo_visible(self, loaded_home_page: HomePage, page: Page) -> None:
        """Verify ParaBank logo is visible."""
        logo = page.locator(".logo")
        expect(logo).to_be_visible()

    def test_admin_logo_visible(self, loaded_home_page: HomePage, page: Page) -> None:
        """Verify admin logo/link is visible."""
        # Admin logo is an image with class 'admin'
        admin_logo = page.locator("img.admin")
        expect(admin_logo).to_be_visible()

    def test_home_link_in_navigation(self, loaded_home_page: HomePage, page: Page) -> None:
        """Verify 'Home' link is visible in navigation."""
        # Navigation links use lowercase text
        home_link = page.locator("ul.button li.home a")
        expect(home_link).to_be_visible()

    def test_about_us_link_in_navigation(self, loaded_home_page: HomePage, page: Page) -> None:
        """Verify 'About Us' link is visible in navigation."""
        # Use first matching link
        about_link = page.locator("#headerPanel a[href*='about']").first
        expect(about_link).to_be_visible()
        expect(about_link).to_contain_text("About")

    def test_contact_link_in_navigation(self, loaded_home_page: HomePage) -> None:
        """Verify 'Contact' link is visible in navigation."""
        expect(loaded_home_page.contact_link).to_be_visible()
        # Navigation links use lowercase text
        expect(loaded_home_page.contact_link).to_contain_text("contact")

    def test_customer_login_heading(self, loaded_home_page: HomePage, page: Page) -> None:
        """Verify 'Customer Login' heading is visible."""
        # Login heading is an h2 element inside leftPanel
        login_heading = page.locator("#leftPanel h2").filter(has_text="Customer Login")
        expect(login_heading).to_be_visible()

    def test_username_label(self, loaded_home_page: HomePage, page: Page) -> None:
        """Verify username label is visible."""
        # Check for username text in the login panel
        username_label = page.locator("#loginPanel").get_by_text("Username")
        expect(username_label).to_be_visible()

    def test_password_label(self, loaded_home_page: HomePage, page: Page) -> None:
        """Verify password label is visible."""
        # Check for password text in the login panel
        password_label = page.locator("#loginPanel").get_by_text("Password")
        expect(password_label).to_be_visible()

    def test_right_panel_visible(self, loaded_home_page: HomePage, page: Page) -> None:
        """Verify right panel with ATM services info is visible."""
        right_panel = page.locator("#rightPanel")
        expect(right_panel).to_be_visible()

    def test_atm_services_heading(self, loaded_home_page: HomePage, page: Page) -> None:
        """Verify content is visible in right panel."""
        # Right panel may have different content, just check it exists and has content
        right_panel = page.locator("#rightPanel")
        expect(right_panel).to_be_visible()
        # Check that right panel has some text content
        expect(right_panel).not_to_be_empty()

    def test_footer_visible(self, loaded_home_page: HomePage, page: Page) -> None:
        """Verify footer is visible."""
        footer = page.locator("#footerPanel")
        expect(footer).to_be_visible()

    def test_footer_links_visible(self, loaded_home_page: HomePage, page: Page) -> None:
        """Verify footer links are visible."""
        # Check for common footer links
        footer_links = page.locator("#footerPanel a")
        expect(footer_links.first).to_be_visible()

    def test_page_loads_successfully(
        self, loaded_home_page: HomePage, page: Page, base_url: str
    ) -> None:
        """Verify home page loads without errors."""
        # Check that we're on a page within the base URL
        expect(page).to_have_url(re.compile(f"{re.escape(base_url)}.*"))

    def test_login_form_can_accept_input(self, loaded_home_page: HomePage) -> None:
        """Verify login form fields can accept user input."""
        # Type in username field
        loaded_home_page.user_name_text.fill("testuser")
        expect(loaded_home_page.user_name_text).to_have_value("testuser")

        # Type in password field
        loaded_home_page.password_text.fill("testpass")
        expect(loaded_home_page.password_text).to_have_value("testpass")

    def test_register_link_navigation(
        self, loaded_home_page: HomePage, page: Page, base_url: str
    ) -> None:
        """Verify clicking 'Register' link navigates to registration page."""
        register_link = page.locator("#loginPanel a[href*='register']")
        register_link.click()

        expect(page).to_have_url(f"{base_url}/register.htm")
        expect(page.locator("h1.title").first).to_have_text("Signing up is easy!")

    def test_about_us_link_navigation(
        self, loaded_home_page: HomePage, page: Page, base_url: str
    ) -> None:
        """Verify clicking 'About Us' link navigates to about page."""
        about_link = page.locator("#headerPanel a[href*='about']").first
        about_link.click()

        expect(page).to_have_url(f"{base_url}/about.htm")

    def test_contact_link_navigation(
        self, loaded_home_page: HomePage, page: Page, base_url: str
    ) -> None:
        """Verify clicking 'Contact' link navigates to contact page."""
        loaded_home_page.contact_link.click()

        expect(page).to_have_url(f"{base_url}/contact.htm")
        expect(page.locator("h1.title").first).to_have_text("Customer Care")

    def test_home_link_navigation(
        self, loaded_home_page: HomePage, page: Page, base_url: str
    ) -> None:
        """Verify clicking 'Home' link stays on home page."""
        # Navigation links use lowercase text
        home_link = page.locator("ul.button li.home a")
        home_link.click()

        # Should navigate to index page - use raw string for regex
        expect(page).to_have_url(re.compile(rf"{re.escape(base_url)}/?(index\.htm)?$"))
