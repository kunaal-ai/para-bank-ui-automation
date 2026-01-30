"""Tests for the Open New Account page."""

import pytest
from playwright.sync_api import Page, expect

from src.utils.stability import safe_click
from tests.pages.helper_pom.payment_services_tab import PaymentServicesTab
from tests.pages.open_account_page import OpenAccountPage


def _expected_open_account_url(base_url: str) -> str:
    """Build the expected open account URL for the given base URL."""
    if base_url.endswith("/"):
        return f"{base_url}openaccount.htm"
    return f"{base_url}/openaccount.htm"


@pytest.mark.flaky
def test_open_checking_account(
    user_login: None,
    payment_services_tab: PaymentServicesTab,
    open_account_page: OpenAccountPage,
    page: Page,
    base_url: str,
) -> None:
    """Open a new CHECKING account from an existing account."""
    safe_click(payment_services_tab.open_new_account_link)

    page.wait_for_url("**/openaccount.htm", timeout=10000)
    page.wait_for_load_state("networkidle", timeout=5000)

    expected_url = _expected_open_account_url(base_url)
    expect(page).to_have_url(expected_url)

    open_account_page.open_new_account(
        account_type="CHECKING",
        from_account_index=0,
    )

    expect(page).to_have_url(expected_url)
    expect(open_account_page.account_opened_heading).to_have_text("Account Opened!")
    expect(open_account_page.account_opened_message).to_have_text(
        "Congratulations, your account is now open."
    )


@pytest.mark.flaky
def test_open_savings_account(
    user_login: None,
    payment_services_tab: PaymentServicesTab,
    open_account_page: OpenAccountPage,
    page: Page,
    base_url: str,
) -> None:
    """Open a new SAVING/SAVINGS account from an existing account."""
    safe_click(payment_services_tab.open_new_account_link)

    page.wait_for_url("**/openaccount.htm", timeout=10000)
    page.wait_for_load_state("networkidle", timeout=5000)

    expected_url = _expected_open_account_url(base_url)
    expect(page).to_have_url(expected_url)

    open_account_page.open_new_account(
        account_type="SAVING",
        from_account_index=0,
    )

    expect(page).to_have_url(expected_url)
    expect(open_account_page.account_opened_heading).to_have_text("Account Opened!")
    expect(open_account_page.account_opened_message).to_have_text(
        "Congratulations, your account is now open."
    )


@pytest.mark.flaky
def test_open_account_type_options(
    user_login: None,
    payment_services_tab: PaymentServicesTab,
    open_account_page: OpenAccountPage,
) -> None:
    """Verify that both Checking and Savings account types are available."""
    safe_click(payment_services_tab.open_new_account_link)

    options = open_account_page.account_type_select.locator("option").all_inner_texts()
    assert "CHECKING" in [o.upper() for o in options]
    assert any("SAVING" in o.upper() for o in options)
