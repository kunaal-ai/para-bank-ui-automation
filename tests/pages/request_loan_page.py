"""Request Loan Page Object."""
import logging

from playwright.sync_api import Page, expect

logger = logging.getLogger("parabank")


class RequestLoanPage:
    """Request Loan Page Object."""

    def __init__(self, page: Page) -> None:
        self.page = page
        self.amount_input = page.locator("#amount")
        self.down_payment_input = page.locator("#downPayment")
        self.from_account_dropdown = page.locator("#fromAccountId")
        self.apply_button = page.locator("input[value='Apply Now']")
        self.status_text = page.locator("#loanStatus")
        self.result_container = page.locator("#requestLoanResult")

    def apply_for_loan(
        self, amount: str, down_payment: str, from_account: str | None = None
    ) -> None:
        """Fill out and submit the loan application form."""
        logger.info(f"Applying for loan: amount={amount}, down_payment={down_payment}")
        self.amount_input.fill(amount)
        self.down_payment_input.fill(down_payment)

        if from_account:
            self.from_account_dropdown.select_option(label=from_account)

        self.apply_button.click()

    def get_loan_status(self) -> str:
        """Get the status of the loan application."""
        expect(self.status_text).to_be_visible()
        status = self.status_text.inner_text()
        logger.info(f"Loan status: {status}")
        return str(status)

    def is_loan_approved(self) -> bool:
        """Check if the loan was approved."""
        status = self.get_loan_status()
        return "Approved" in status

    def is_loan_denied(self) -> bool:
        """Check if the loan was denied."""
        status = self.get_loan_status()
        return "Denied" in status
