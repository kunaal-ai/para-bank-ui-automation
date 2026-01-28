"""Payment Services Tab page object."""
from playwright.sync_api import Page


class PaymentServicesTab:
    """Payment Services Tab page object."""

    def __init__(self, page: Page) -> None:
        self.page = page
        self.left_panel = page.locator("#leftPanel")

        self.open_new_account_link = self.left_panel.get_by_role("link", name="Open New Account")
        self.accounts_overview_link = self.left_panel.get_by_role("link", name="Accounts Overview")
        self.transfer_funds_link = self.left_panel.get_by_role("link", name="Transfer Funds")
        self.bill_pay_link = self.left_panel.get_by_role("link", name="Bill Pay")
        self.find_transactions_link = self.left_panel.get_by_role("link", name="Find Transactions")
        self.update_contact_info_link = self.left_panel.get_by_role(
            "link", name="Update Contact Info"
        )
        self.request_loan_link = self.left_panel.get_by_role("link", name="Request Loan")
        self.log_out_link = self.left_panel.get_by_role("link", name="Log Out")
