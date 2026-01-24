"""Tests for Home Page"""
from playwright.sync_api import Page, expect

from tests.pages.home_login_page import HomePage


def test_user_log_in_sucessfully(page: Page, base_url: str, env_config: dict) -> None:
    page.goto(base_url)
    page.wait_for_selector("input[name='username']", state="visible")

    # Get test user credentials from config
    test_user = env_config["users"]["valid"]

    page.fill("input[name='username']", test_user["username"])
    page.fill("input[name='password']", test_user["password"])
    page.click("input[value='Log In']")

    page.wait_for_url("**/overview.htm")
    expect(page.locator("#showOverview h1.title")).to_have_text("Accounts Overview")


def test_forget_login(home_page: HomePage, page: Page, base_url: str) -> None:
    home_page.forget_login()
    expect(page).to_have_url(f"{base_url}/lookup.htm")
    expect(page.locator("h1.title")).to_have_text("Customer Lookup")
