"""Tests for Home Page"""
from playwright.sync_api import Page, expect
import pytest
from tests.pages.home_login_page import HomePage


def test_user_log_in_sucessfully(page: Page, base_url: str, env_config):
    """Verify if user is logged in successfully."""
    # Navigate to the login page
    page.goto(base_url)
    
    # Wait for the login form to be visible
    page.wait_for_selector("input[name='username']", state="visible", timeout=10000)
    
    # Get test user credentials from config
    test_user = env_config['users']['valid']
    
    # Perform login
    page.fill("input[name='username']", test_user['username'])
    page.fill("input[name='password']", test_user['password'])
    page.click("input[value='Log In']")
    
    # Wait for navigation and verify
    page.wait_for_url("**/overview.htm", timeout=10000)
    expect(page.locator("#showOverview h1.title")).to_have_text("Accounts Overview")

def test_forget_login(home_page, page: Page, base_url: str):
    """Test the forget login functionality using fixture.
    
    Args:
        home_page: Pre-initialized HomePage fixture
        page: Playwright page object
        base_url: Base URL of the application
    """
    home_page.forget_login()
    expect(page).to_have_url(f"{base_url}/lookup.htm")
    expect(page.locator("h1.title")).to_have_text("Customer Lookup")
