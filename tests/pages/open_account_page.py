"""Page objects for Open Account page."""

from typing import Optional

from playwright.sync_api import Page

from src.utils.stability import wait_for_options


class OpenAccountPage:
    """Page object model for the Open New Account page."""

    def __init__(self, page: Page) -> None:
        self.page = page
        self.account_type_select = page.locator("select#type")
        self.from_account_select = page.locator("select#fromAccountId")
        self.open_new_account_button = page.locator("input.button[value='Open New Account']")
        self.account_opened_heading = page.get_by_role("heading", name="Account Opened!")
        self.account_opened_message = page.get_by_text("Congratulations, your account is now open.")

    def select_account_type(self, account_type: str) -> None:
        """Select account type, handling both 'SAVING' and 'SAVINGS' labels."""
        wait_for_options(self.account_type_select, min_options=2)

        # ParaBank sometimes uses 'SAVING' and sometimes 'SAVINGS'
        if account_type.upper() in ["SAVING", "SAVINGS"]:
            # Try to select whichever one matches the available options
            try:
                self.account_type_select.select_option(label="SAVING")
            except Exception:
                self.account_type_select.select_option(label="SAVINGS")
        else:
            self.account_type_select.select_option(label=account_type.upper())

    def select_from_account_by_index(self, index: int = 0) -> None:
        """Select a source account by index in the dropdown."""
        wait_for_options(self.from_account_select, min_options=1)
        self.from_account_select.select_option(index=index)

    def open_new_account(
        self,
        account_type: str = "CHECKING",
        from_account_index: Optional[int] = None,
    ) -> None:
        """Open a new account."""
        self.select_account_type(account_type)
        if from_account_index is not None:
            self.select_from_account_by_index(from_account_index)
        self.open_new_account_button.click()
        self.account_opened_heading.wait_for(state="visible", timeout=10000)
