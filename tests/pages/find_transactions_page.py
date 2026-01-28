"""Find Transactions Page Object."""
import logging

from playwright.sync_api import Page, expect

logger = logging.getLogger("parabank")


class FindTransactionsPage:
    """Find Transactions Page Object."""

    def __init__(self, page: Page) -> None:
        self.page = page
        self.account_select = page.locator("#accountId").or_(
            page.locator('select[name="accountId"]')
        )
        self.transaction_id_input = page.locator("#transactionId")
        self.find_by_id_button = page.locator("#findById")

        self.date_input = page.locator("#transactionDate")
        self.find_by_date_button = page.locator("#findByDate")

        self.amount_input = page.locator("#amount")
        self.find_by_amount_button = page.locator("#findByAmount")

        self.transaction_table = page.locator("#transactionTable")
        self.id_error = page.locator("#transactionIdError")
        self.date_error = page.locator("#transactionDateError")

    def find_by_id(self, transaction_id: str) -> None:
        """Find transaction by ID."""
        logger.info(f"Finding transaction by ID: {transaction_id}")
        self.transaction_id_input.fill(transaction_id)
        self.find_by_id_button.click()

    def find_by_date(self, date: str) -> None:
        """Find transactions by date (format: MM-DD-YYYY)."""
        logger.info(f"Finding transactions by date: {date}")
        self.date_input.fill(date)
        self.date_input.press("Enter")
        # Fallback click if Enter is not enough
        if not self.transaction_table.is_visible():
            self.find_by_date_button.click()

    def find_by_amount(self, amount: str) -> None:
        """Find transactions by amount."""
        logger.info(f"Finding transactions by amount: {amount}")
        self.amount_input.fill(amount)
        self.amount_input.press("Enter")
        # Fallback click if Enter is not enough
        if not self.transaction_table.is_visible():
            self.find_by_amount_button.click()

    def wait_for_results(self) -> None:
        """Wait for the transaction table or a no results message to be visible."""
        # ParaBank might show a table or a message like "No transactions found"
        results_locator = self.transaction_table.or_(self.page.get_by_text("No transactions found"))
        expect(results_locator).to_be_visible(timeout=10000)
        logger.info("Transaction search results (or no results message) loaded.")
