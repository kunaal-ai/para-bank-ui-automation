"""Payment Services Tab page object."""
from playwright.sync_api import Page


class PaymentServicesTab:
    """Payment Services Tab page object."""

    def __init__(self, page: Page) -> None:
        self.page = page
        self.open_new_account_link = page.get_by_role("link", name="Open New Account")
        self.accounts_overview_link = page.get_by_role("link", name="Accounts Overview")
        self.transfer_funds_link = page.get_by_role("link", name="Transfer Funds")
        self.bill_pay_link = page.get_by_role("link", name="Bill Pay")
        self.find_tranactions_link = page.get_by_role("link", name="Find Transactions")
        self.update_contact_info_link = page.get_by_role("link", name="Update Contact Info")
        self.request_loan_link = page.get_by_role("link", name="Request Loan")
        self.log_out_link = page.get_by_role("link", name="Log Out")
