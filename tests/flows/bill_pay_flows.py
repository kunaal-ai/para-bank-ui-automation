"""Business workflows for Bill Pay."""

from playwright.sync_api import Page

from tests.pages.bill_pay_page import BillPayPage


class BillPayFlows:
    """Business-level workflows for paying bills."""

    def __init__(self, page: Page) -> None:
        self.page = page
        self.bill_pay_page = BillPayPage(page)

    def pay_bill(
        self,
        payee_name: str,
        address: str,
        city: str,
        state: str,
        zip_code: str,
        phone_no: str,
        from_account: str,
        amount: str,
    ) -> None:
        """Execute the business flow for paying a bill."""
        self.bill_pay_page.submit_form(
            name=payee_name,
            address=address,
            city=city,
            state=state,
            zip_code=zip_code,
            phone_no=phone_no,
            account_no=from_account,
            verify_acc_no=from_account,
            amount=amount,
        )
