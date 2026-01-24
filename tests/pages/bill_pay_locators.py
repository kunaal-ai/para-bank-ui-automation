"""Locators for the Bill Pay page."""

from playwright.sync_api import Locator, Page


class BillPayLocators:
    """Locators for the Bill Pay page."""

    def __init__(self, page: Page) -> None:
        self.name_text: Locator = page.locator("input[name='payee.name']")
        self.address_text: Locator = page.locator("input[name='payee.address.street']")
        self.city_text: Locator = page.locator("input[name='payee.address.city']")
        self.state_text: Locator = page.locator("input[name='payee.address.state']")
        self.zip_code_text: Locator = page.locator("input[name='payee.address.zipCode']")
        self.phone_no_text: Locator = page.locator("input[name='payee.phoneNumber']")
        self.account_no: Locator = page.locator("input[name='payee.accountNumber']")
        self.verify_acc_no_text: Locator = page.locator("input[name='verifyAccount']")
        self.amount_text: Locator = page.locator("input[name='amount']")
        self.send_payment_button: Locator = page.locator("input.button")
