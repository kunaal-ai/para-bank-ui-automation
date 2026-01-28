"""Account Overview Page Object."""
import logging

from playwright.sync_api import Page, expect

logger = logging.getLogger("parabank")


class AccountOverviewPage:
    """Account Overview Page Object."""

    def __init__(self, page: Page) -> None:
        self.page = page
        self.title = page.locator("#rightPanel h1.title").first
        self.account_table = page.locator("#accountTable")
        self.first_account_link = page.locator("#accountTable tbody tr:first-child td a")
        self.first_account_balance = page.locator(
            "#accountTable tbody tr:first-child td:nth-child(2)"
        )

    def wait_for_data(self) -> None:
        """Wait for the account data to be visible."""
        expect(self.account_table).to_be_visible(timeout=10000)
        expect(self.first_account_link).to_be_visible(timeout=10000)
        logger.info("Account Overview data loaded.")

    def get_first_account_number(self) -> str:
        """Get the first account number text."""
        self.wait_for_data()
        return str(self.first_account_link.inner_text())

    def get_first_account_balance(self) -> str:
        """Get the first account balance text."""
        self.wait_for_data()
        return str(self.first_account_balance.inner_text())

    def click_first_account(self) -> None:
        """Click on the first account number link."""
        self.wait_for_data()
        self.first_account_link.click()
