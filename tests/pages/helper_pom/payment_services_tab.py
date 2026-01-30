from playwright.sync_api import Page

from src.utils.stability import safe_click, skip_if_internal_error


class PaymentServicesTab:
    """Payment Services Tab page object with robust navigation."""

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

    def navigate_to(self, link_name: str) -> None:
        """Centralized robust navigation."""
        links = {
            "open_new_account": self.open_new_account_link,
            "accounts_overview": self.accounts_overview_link,
            "transfer_funds": self.transfer_funds_link,
            "bill_pay": self.bill_pay_link,
            "find_transactions": self.find_transactions_link,
            "update_contact": self.update_contact_info_link,
            "request_loan": self.request_loan_link,
            "logout": self.log_out_link,
        }

        if link_name in links:
            safe_click(links[link_name])
            # Automatically check for internal errors after every side-menu navigation
            self.page.wait_for_load_state("load")
            skip_if_internal_error(self.page)
        else:
            raise ValueError(f"Unknown navigation link: {link_name}")
