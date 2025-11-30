"""Test login functionality."""
import pytest
from playwright.sync_api import Page, expect
from tests.pages.home_login_page import HomePage


def test_login_successful(page: Page, env_config, base_url: str):
    """Test successful login using environment configuration."""
    # Get test user credentials from config
    test_user = env_config['users']['valid']
    
    # Create page object
    home_page = HomePage(page)
    
    # Navigate to the home page
    home_page.load(base_url)
    
    # Verify we're on the login page
    expect(page).to_have_title("ParaBank | Welcome | Online Banking")
    
    # Perform login using credentials from config
    home_page.user_log_in(test_user['username'], test_user['password'])
    
    # Wait for all network requests to complete
    page.wait_for_load_state('networkidle')
    
    # Check for any error messages
    error_message = page.locator("p.error")
    if error_message.is_visible():
        error_text = error_message.text_content()
        pytest.fail(f"Login failed with error: {error_text}")
    
    # Verify successful login
    expected_url = f"{base_url}overview.htm" if base_url.endswith('/') else f"{base_url}/overview.htm"
    expect(page).to_have_url(expected_url)
    
    # Verify welcome message with a specific locator
    welcome_msg = page.locator("h1.title:has-text('Accounts Overview')")
    expect(welcome_msg).to_be_visible()