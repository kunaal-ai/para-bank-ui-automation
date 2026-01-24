"""Testing bill payment for submission."""
import logging

from playwright.sync_api import Page, expect

from tests.pages.bill_pay_page import BillPayPage
from tests.pages.helper_pom.payment_services_tab import PaymentServicesTab

logger = logging.getLogger("parabank")


def test_submit_form_with_correct_values(
    user_login: None,
    payment_services_tab: PaymentServicesTab,
    bill_pay_page: BillPayPage,
    page: Page,
    base_url: str,
) -> None:
    payment_services_tab.bill_pay_link.click()

    test_data = {
        "name": "Test Payee",
        "address": "123 Test St",
        "city": "Test City",
        "state": "CA",
        "zip_code": "12345",
        "phone_no": "1234567890",
        "account_no": "221144",
        "verify_acc_no": "221144",
        "amount": "9786.00",
    }
    bill_pay_page.submit_form(**test_data)

    expect(page.locator("#billpayResult h1.title")).to_have_text("Bill Payment Complete")
