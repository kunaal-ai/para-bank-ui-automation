""" Page objects for BillPay class
"""

from playwright.sync_api import Page


class BillPay:
    """_summary_
    """
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
        self.send_payment_button = page.locator('input.button')

    
    def submit_form(
        self,
        name,
        address,
        city,
        state,
        zip_code,
        phone_no,
        account_no,
        verify_acc_no,
        amount,
    ):
        """Submit pay form

        Args:
            name (any): Expected string input in form
            address (any): Expected string input in form
            city (any): Expected string input in form
            state (any): Expected string input in form
            zip_code (any): Expected string input in form
            phone_no (any): Expected string input in form
            account_no (any): Expected string input in form
            verify_acc_no (any): Expected string input in form
            amount (any): Expected string input in form
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
