"""Tests for Home Page"""
import pytest
from playwright.sync_api import Page, expect

from src.utils.stability import handle_internal_error, safe_click
from tests.pages.home_login_page import HomePage


@pytest.mark.flaky
def test_user_log_in_successfully(page: Page, base_url: str, env_config: dict) -> None:
    """Test successful user login using HomePage."""
    home_page = HomePage(page)
    home_page.load(base_url)

    # Get test user credentials from config
    test_user = env_config["users"]["valid"]

    # Use HomePage's login method which includes conditional pass logic
    home_page.user_log_in(test_user["username"], test_user["password"])

    # Wait for the overview section to be visible
    page.wait_for_selector("#showOverview", state="visible", timeout=15000)
    expect(page.locator("#showOverview h1.title")).to_have_text("Accounts Overview")


@pytest.mark.flaky
def test_forget_login(home_page: HomePage, page: Page, base_url: str) -> None:
    # If already logged in, log out first to ensure the button is visible
    logout_link = page.get_by_role("link", name="Log Out")
    if logout_link.is_visible(timeout=2000):
        logout_link.click()
        page.wait_for_url(base_url)

    # Use safe_click for the forgot login link
    safe_click(home_page.forget_login_button)

    # Check for internal errors
    handle_internal_error(page, requires_login=False)

    # Wait for the navigation
    page.wait_for_url("**/lookup.htm", timeout=15000)
    expect(page).to_have_url(f"{base_url}/lookup.htm")
    expect(page.locator("h1.title")).to_have_text("Customer Lookup")
