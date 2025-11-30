"""Tests for Home Page"""
from playwright.sync_api import Page, expect
import pytest
from tests.pages.home_login_page import HomePage


def test_user_log_in_sucessfully(user_login, page: Page):
    """Verify if user is landed on its page after entering correct credentials

    Args:
        user_login: Fixture that handles user login
        page: Playwright page object
    """
    expect(page).to_have_url("/parabank/overview.htm")


@pytest.mark.skip()
def test_forget_login(user_login, page: Page):
    """Click on forget login and verify page

    Args:
        user_login: Fixture that handles user login
        page: Playwright page object
    """
    expect(page).to_have_url("/parabank/lookup.htm")
