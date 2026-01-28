from playwright.sync_api import Page, expect

from src.utils.stability import skip_if_internal_error
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


def test_login_invalid_credentials(page: Page, base_url: str) -> None:
    """Test login failure with invalid credentials."""
    home_page = HomePage(page)
    home_page.load(base_url)

    # Ensure we are logged out
    if page.get_by_role("link", name="Log Out").is_visible():
        page.get_by_role("link", name="Log Out").click()
        home_page.load(base_url)

    home_page.user_log_in("invalid_user", "invalid_password", assert_success=False)
    skip_if_internal_error(page)

    error_locator = page.locator("p.error").first
    expected_msg = "The username and password could not be verified."

    expect(error_locator).to_be_visible(timeout=10000)
    actual_text = error_locator.inner_text()
    assert expected_msg in actual_text


def test_login_empty_credentials(page: Page, base_url: str) -> None:
    """Test login with empty credentials."""
    home_page = HomePage(page)
    home_page.load(base_url)
    home_page.user_log_in("", "", assert_success=False)
    expect(home_page.error_message).to_be_visible()
    expect(home_page.error_message).to_have_text("Please enter a username and password.")


def test_forgot_login_info_navigation(page: Page, base_url: str) -> None:
    """Test navigation to the Forgot Login Information page."""
    home_page = HomePage(page)
    home_page.load(base_url)
    home_page.forget_login_button.click()
    expect(page.locator("h1.title")).to_have_text("Customer Lookup")


def test_login_after_logout(page: Page, env_config: dict, base_url: str) -> None:
    """Test login functionality after a successful logout."""
    test_user = env_config["users"]["valid"]
    home_page = HomePage(page)
    home_page.load(base_url)
    home_page.user_log_in(test_user["username"], test_user["password"])

    page.get_by_role("link", name="Log Out").click()
    import re

    expect(page).to_have_url(re.compile(r".*/(index|logout)\.htm"))

    home_page.user_log_in(test_user["username"], test_user["password"])
    expect(page.locator("h1.title:has-text('Accounts Overview')")).to_be_visible()
