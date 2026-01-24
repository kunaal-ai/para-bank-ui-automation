"""Page actions for the Bill Pay page."""

from playwright.sync_api import Page

from .bill_pay_locators import BillPayLocators


class BillPayPage:
    """Low-level interactions with the Bill Pay page (no business rules)."""

    def __init__(self, page: Page) -> None:
        self.page = page
        self.locators = BillPayLocators(page)

    def fill_name(self, name: str) -> None:
        self.locators.name_text.fill(name)

    def fill_address(self, address: str) -> None:
        self.locators.address_text.fill(address)

    def fill_city(self, city: str) -> None:
        self.locators.city_text.fill(city)

    def fill_state(self, state: str) -> None:
        self.locators.state_text.fill(state)

    def fill_zip_code(self, zip_code: str) -> None:
        self.locators.zip_code_text.fill(zip_code)

    def fill_phone_no(self, phone_no: str) -> None:
        self.locators.phone_no_text.fill(phone_no)

    def fill_account_no(self, account_no: str) -> None:
        self.locators.account_no.fill(account_no)

    def fill_verify_account_no(self, verify_acc_no: str) -> None:
        self.locators.verify_acc_no_text.fill(verify_acc_no)

    def fill_amount(self, amount: str) -> None:
        self.locators.amount_text.fill(amount)

    def click_send_payment(self) -> None:
        self.locators.send_payment_button.click()

    def submit_form(
        self,
        name: str,
        address: str,
        city: str,
        state: str,
        zip_code: str,
        phone_no: str,
        account_no: str,
        verify_acc_no: str,
        amount: str,
    ) -> None:
        self.fill_name(name)
        self.fill_address(address)
        self.fill_city(city)
        self.fill_state(state)
        self.fill_zip_code(zip_code)
        self.fill_phone_no(phone_no)
        self.fill_account_no(account_no)
        self.fill_verify_account_no(verify_acc_no)
        self.fill_amount(amount)
        self.click_send_payment()
