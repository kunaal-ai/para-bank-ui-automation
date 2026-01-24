"""Tests for the Logout functionality."""
import pytest
from playwright.sync_api import Page, expect

from tests.pages.helper_pom.payment_services_tab import PaymentServicesTab


@pytest.mark.usefixtures("user_login")
def test_logout_successful(page: Page, payment_services_tab: PaymentServicesTab) -> None:
    """Verify that the user can log out successfully."""
    # Logout
    payment_services_tab.log_out_link.click()

    # Verify we are on the login page/home page
    expect(page.locator("input[name='username']")).to_be_visible()
    expect(page.locator("input[name='password']")).to_be_visible()
