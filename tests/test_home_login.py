"""Tests for Home Page
"""
from playwright.sync_api import Page, expect
import pytest

def test_user_log_in_sucessfully(user_login, page: Page):
    """Verify if user is landed on its page after entering correct credentials

    Args:
        home_page (_type_): class HomePage object
        page (Page): page object
    """

    expect(page).to_have_url("/parabank/overview.htm")


@pytest.mark.skip()
def test_forget_login(user_login, page: Page):
    """click on forget login and verify page

    Args:
        home_page (_type_): fixture, class HomePage object
        page (Page): page object
    """

    expect(page).to_have_url("/parabank/lookup.htm")
