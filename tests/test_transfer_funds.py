"""Test transfer funds functionality."""

import logging
import re

import pytest
from playwright.sync_api import Page, expect

from src.utils.stability import safe_click
from tests.pages.transfer_funds_page import TransferFundsPage

logger = logging.getLogger("parabank")


@pytest.mark.flaky
def test_transfer_funds_success(
    user_login: None,
    payment_services_tab: object,
    page: Page,
    base_url: str,
) -> None:
    safe_click(payment_services_tab.transfer_funds_link)
    page.wait_for_url("**/transfer.htm")

    transfer_page = TransferFundsPage(page)
    page.wait_for_selector("input#amount")

    transfer_page.amount_input.fill("100.00")

    # Wait for options to be populated with numeric account IDs
    expect(transfer_page.from_account_select.locator("option").first).to_contain_text(
        re.compile(r"\d+")
    )
    transfer_page.from_account_select.select_option(index=0)

    expect(transfer_page.to_account_select.locator("option").first).to_contain_text(
        re.compile(r"\d+")
    )
    transfer_page.to_account_select.select_option(index=0)

    transfer_page.transfer_button.click()

    transfer_page.verify_success()
    expect(page.locator("h1.title:visible")).not_to_have_text("Transfer Funds")


@pytest.mark.flaky
def test_transfer_funds_empty_amount(
    user_login: None,
    payment_services_tab: object,
    page: Page,
) -> None:
    """Test fund transfer with an empty amount."""
    payment_services_tab.transfer_funds_link.click()
    transfer_page = TransferFundsPage(page)
    page.wait_for_selector("input#amount")

    # Click transfer without filling amount
    transfer_page.transfer_button.click()

    # Check if we are still on the same page or if an error is shown
    expect(page.locator("h1.title").first).to_have_text("Transfer Funds")


@pytest.mark.flaky
def test_transfer_funds_navigation_and_fields(
    user_login: None,
    payment_services_tab: object,
    page: Page,
) -> None:
    """Test navigation to transfer funds and presence of necessary fields."""
    safe_click(payment_services_tab.transfer_funds_link)
    transfer_page = TransferFundsPage(page)

    expect(transfer_page.amount_input).to_be_visible()
    expect(transfer_page.from_account_select).to_be_visible()
    expect(transfer_page.to_account_select).to_be_visible()
    expect(transfer_page.transfer_button).to_be_visible()
