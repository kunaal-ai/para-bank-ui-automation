"""Test login functionality."""
from playwright.sync_api import Page, expect

from tests.pages.home_login_page import HomePage


def test_login_successful(page: Page, env_config: dict, base_url: str) -> None:
    """Test successful login using environment configuration."""
    # Get test user credentials from config
    test_user = env_config["users"]["valid"]
    home_page = HomePage(page)
    home_page.load(base_url)

    expect(page).to_have_title("ParaBank | Welcome | Online Banking")

    home_page.user_log_in(test_user["username"], test_user["password"])
    page.wait_for_load_state("networkidle")

    expected_url = f"{base_url.rstrip('/')}/overview.htm"
    expect(page).to_have_url(expected_url)
    expect(page.locator("h1.title:has-text('Accounts Overview')")).to_be_visible()
