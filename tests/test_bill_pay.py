"""Testing bill payment for submission.
"""


def test_submit_form_with_correct_values(
    home_page, payment_services_tab, bill_pay_page
):
    """Send valid inputs and submit form

    Args:
        user_login (fixture): log in user with correct credentials
        payment_services_tab (fixture): Instance of PaymentServicesTab class
        bill_pay_page (fixture): Instance of BillPay class
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
