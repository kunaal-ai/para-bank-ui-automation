"""Page objects for BillPay class."""

from playwright.sync_api import Page


class BillPay:
    """_summary_"""

    def __init__(self, page: Page) -> None:
        self.page = page
        self.name_text = page.locator("input[name='payee.name']")
        self.address_text = page.locator("input[name='payee.address.street' ]")
        self.city_text = page.locator("input[name='payee.address.city' ]")
        self.state_text = page.locator("input[name='payee.address.state' ]")
        self.zip_code_text = page.locator("input[name='payee.address.zipCode' ]")
        self.phone_no_text = page.locator("input[name='payee.phoneNumber' ]")
        self.account_no = page.locator("input[name='payee.accountNumber' ]")
        self.verify_acc_no_text = page.locator("input[name='verifyAccount' ]")
        self.amount_text = page.locator("input[name='amount' ]")
        self.send_payment_button = page.locator("input.button")

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
        """Submit pay form

        Args:
            name: Payee name
            address: Payee street address
            city: Payee city
            state: Payee state
            zip_code: Payee ZIP code
            phone_no: Payee phone number
            account_no: Payee account number
            verify_acc_no: Verification of account number
            amount: Payment amount
        """
        self.name_text.fill(name)
        self.address_text.fill(address)
        self.city_text.fill(city)
        self.state_text.fill(state)
        self.zip_code_text.fill(zip_code)
        self.phone_no_text.fill(phone_no)
        self.account_no.fill(account_no)
        self.verify_acc_no_text.fill(verify_acc_no)
        self.amount_text.fill(amount)
        self.send_payment_button.click()
