"""Testing bill payment for submission.
"""
import pytest

from tests.pages.bill_pay_page import BillPay
from tests.pages.home_login_page import HomePage
from tests.pages.helper_pom.payment_services_tab import PaymentServicesTab

def test_submit_form_with_correct_values(
    home_page: HomePage,
    payment_services_tab: PaymentServicesTab,
    bill_pay_page: BillPay
):
    """Send valid inputs and submit form

    Args:
        home_page: Instance of HomePage class
        payment_services_tab: Instance of PaymentServicesTab class
        bill_pay_page: Instance of BillPay class
    """    
    home_page.load()
    home_page.user_log_in()
    payment_services_tab.bill_pay_link.click()

    bill_pay_page.submit_form(
        "test",
        "address XYZ",
        "city CTY",
        "Ohio",
        "12345",
        "9998887766",
        "221144",
        "221144",
        "9786",
    )
