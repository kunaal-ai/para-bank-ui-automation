"""Test transfer funds functionality."""

import logging
import re

from playwright.sync_api import Page, expect

from tests.pages.transfer_funds_page import TransferFundsPage

logger = logging.getLogger("parabank")


def test_transfer_funds_success(
    user_login: None,
    payment_services_tab: object,
    page: Page,
    base_url: str,
) -> None:
    payment_services_tab.transfer_funds_link.click()
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
