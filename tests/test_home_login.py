"""Tests for Home Page"""
import pytest
from playwright.sync_api import Page, expect

from tests.pages.home_login_page import HomePage


@pytest.mark.flaky
def test_user_log_in_sucessfully(page: Page, base_url: str, env_config: dict) -> None:
    """Test successful user login using HomePage."""
    home_page = HomePage(page)
    home_page.load(base_url)

    # Get test user credentials from config
    test_user = env_config["users"]["valid"]

    # Use HomePage's login method which includes conditional pass logic
    home_page.user_log_in(test_user["username"], test_user["password"])

    expect(page.locator("#showOverview h1.title")).to_have_text("Accounts Overview")


@pytest.mark.flaky
def test_forget_login(home_page: HomePage, page: Page, base_url: str) -> None:
    home_page.forget_login()
    expect(page).to_have_url(f"{base_url}/lookup.htm")
    expect(page.locator("h1.title")).to_have_text("Customer Lookup")
