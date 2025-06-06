"""Test login functionality."""
import os
import re
import pytest
from dotenv import load_dotenv, find_dotenv
from playwright.sync_api import Page, expect
from pages.home_login_page import HomePage

# Load environment variables from .env file if it exists
env_path = find_dotenv(usecwd=True)
if env_path:
    load_dotenv(dotenv_path=env_path)

# Get credentials from environment variables
TEST_USERNAME = "john"
TEST_PASSWORD = os.environ.get("PASSWORD")

if not TEST_PASSWORD and os.environ.get("JENKINS_HOME"):
    # In Jenkins, the password might be in a different environment variable
    TEST_PASSWORD = os.environ.get("PASSWORD")

if not TEST_PASSWORD:
    print("Warning: PASSWORD environment variable is not set. Tests requiring authentication will fail.")


def test_login_successful(page: Page, base_url: str):
    """Test successful login."""
    # Create page object
    home_page = HomePage(page)
    
    # Navigate to the home page
    home_page.load(base_url)
    
    # Verify we're on the login page
    expect(page).to_have_title("ParaBank | Welcome | Online Banking")
    
    # Verify credentials are loaded
    if not TEST_PASSWORD:
        pytest.fail("PASSWORD environment variable is not set in .env file")
        
    # Perform login with credentials from .env
    home_page.user_log_in(username=TEST_USERNAME, password=TEST_PASSWORD)
    
    # Verify successful login by checking the URL
    expect(page).to_have_url(re.compile(r'.*overview\.htm$'))
    
    # Wait for the page to fully load
    page.wait_for_load_state('networkidle')
    
    # Check for error message first
    error_message = page.locator("p.error")
    if error_message.is_visible():
        error_text = error_message.text_content()
        pytest.fail(f"Login failed with error: {error_text}")
    
    # Verify welcome message using a more specific selector
    welcome_msg = page.locator("h1.title:has-text('Accounts Overview')")
    expect(welcome_msg).to_be_visible()
