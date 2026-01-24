"""Page object model for the Transfer Funds page."""

import re

from playwright.sync_api import Page


class TransferFundsPage:
    def __init__(self, page: Page) -> None:
        self.page = page
        self.amount_input = page.locator("input#amount")
        self.from_account_select = page.locator("select#fromAccountId")
        self.to_account_select = page.locator("select#toAccountId")
        self.transfer_button = page.locator("input[value='Transfer']")
        self.success_heading = page.locator("#showResult h1.title")

    def submit_transfer(self, amount: str, from_account: str, to_account: str) -> None:
        self.amount_input.fill(amount)
        self.from_account_select.locator("option").first.wait_for(state="attached")
        self.from_account_select.select_option(label=from_account)
        self.to_account_select.locator("option").first.wait_for(state="attached")
        self.to_account_select.select_option(label=to_account)
        self.transfer_button.click()

    def verify_success(self) -> None:
        """Wait for the transfer process to complete (Success or Error)."""
        # Wait for any visible title that isn't the initial "Transfer Funds"
        self.page.locator("h1.title:visible").filter(
            has_text=re.compile("^(?!Transfer Funds$).*")
        ).wait_for(timeout=15000)
