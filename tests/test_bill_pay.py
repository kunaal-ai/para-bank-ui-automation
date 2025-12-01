"""Testing bill payment for submission.
"""
import logging
logger = logging.getLogger("parabank")

import pytest
from playwright.sync_api import expect, Page

def test_submit_form_with_correct_values(
    user_login, 
    payment_services_tab, 
    bill_pay_page,
    page: Page,
    base_url:str
):
    """Test bill payment with valid inputs.

    Args:
        user_login: Fixture that handles user login
        payment_services_tab: Payment services tab page object
        bill_pay_page: Bill payment page object
        page: Playwright page object
        base_url: Base URL of the application
    """  
    logger.info("Starting bill payment test")
    try:
        payment_services_tab.bill_pay_link.click()
        logger.debug("Clicked on bill pay link")

        payment_services_tab.bill_pay_link.click()

        # Test data
        test_data = {
            "name": "Test Payee",
            "address": "123 Test St",
            "city": "Test City",
            "state": "CA",
            "zip_code": "12345",
            "phone_no": "1234567890",
            "account_no": "221144",
            "verify_acc_no": "221144",
            "amount": "9786.00"
        }
        logger.debug(f"Submitting form with data: {test_data}")
        bill_pay_page.submit_form(**test_data)

        # Verify success
        logger.info("Verifying payment completion")
        expect(page).to_have_url(f"{base_url}/billpay.htm")
        expect(page.locator("#billpayResult h1.title")).to_have_text("Bill Payment Complete")
        logger.info("Test completed successfully")
    except Exception as e:
        logger.error(f"Test failed: {str(e)}", exc_info=True)
        raise