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

        # Validation Errors
        self.name_error: Locator = page.locator("#validationModel-name")
        self.address_error: Locator = page.locator("#validationModel-address")
        self.city_error: Locator = page.locator("#validationModel-city")
        self.state_error: Locator = page.locator("#validationModel-state")
        self.zip_code_error: Locator = page.locator("#validationModel-zipCode")
        self.phone_error: Locator = page.locator("#validationModel-phoneNumber")
        self.account_empty_error: Locator = page.locator("#validationModel-account-empty")
        self.verify_account_empty_error: Locator = page.locator(
            "#validationModel-verifyAccount-empty"
        )
        self.amount_empty_error: Locator = page.locator("#validationModel-amount-empty")
        self.amount_invalid_error: Locator = page.locator("#validationModel-amount-invalid")
        self.verify_account_mismatch_error: Locator = page.locator(
            "#validationModel-verifyAccount-mismatch"
        )
