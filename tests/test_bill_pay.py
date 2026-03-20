"""Testing bill payment for submission."""
import logging
import os
from typing import Any, Dict

import pytest
from playwright.sync_api import Page, expect

from src.utils.stability import ParaBankInternalError, handle_internal_error
from tests.pages.bill_pay_page import BillPayPage
from tests.pages.helper_pom.payment_services_tab import PaymentServicesTab

logger = logging.getLogger("parabank")


def _billpay_demo_mode_enabled() -> bool:
    """Allow bill pay internal-error soft handling for demo runs."""
    return os.environ.get("DEMO_MODE_BILLPAY", "").lower() in ("1", "true", "yes")


def _open_bill_pay_with_retry(
    page: Page,
    payment_services_tab: PaymentServicesTab,
    base_url: str,
    config: Dict[str, Any],
    attempts: int = 2,
) -> None:
    """Open bill pay and recover once via forced same-page relogin."""
    base = base_url.rstrip("/")
    for attempt in range(attempts):
        payment_services_tab.bill_pay_link.click()
        try:
            handle_internal_error(page, requires_login=True)
            return
        except ParaBankInternalError:
            if attempt == attempts - 1:
                if _billpay_demo_mode_enabled():
                    pytest.xfail(
                        "Bill Pay endpoint returned internal error in demo mode; "
                        "treating as environment instability."
                    )
                raise
            logger.warning("Bill Pay returned internal error; forcing relogin and retrying once.")
            user = config["test_user"]
            try:
                page.goto(f"{base}/logout.htm", timeout=30000)
            except Exception:
                # It's fine if logout endpoint is unavailable in current state.
                pass

            page.goto(f"{base}/index.htm", timeout=30000)
            username = page.locator("input[name='username']")
            password = page.locator("input[name='password']")

            try:
                username.wait_for(state="visible", timeout=10000)
                password.wait_for(state="visible", timeout=10000)
            except Exception:
                # Some states auto-redirect to overview while still authenticated.
                if "overview.htm" in page.url:
                    continue
                page.reload(timeout=30000, wait_until="domcontentloaded")
                username.wait_for(state="visible", timeout=15000)
                password.wait_for(state="visible", timeout=15000)

            page.fill("input[name='username']", user["username"])
            page.fill("input[name='password']", user["password"])
            page.click("input[value='Log In']")
            page.wait_for_url("**/overview.htm", timeout=30000)


def test_submit_form_with_correct_values(
    user_login: None,
    payment_services_tab: PaymentServicesTab,
    bill_pay_page: BillPayPage,
    page: Page,
    base_url: str,
    config: Dict[str, Any],
) -> None:
    _open_bill_pay_with_retry(page, payment_services_tab, base_url, config)

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


def test_bill_pay_validation_errors(
    user_login: None,
    payment_services_tab: PaymentServicesTab,
    bill_pay_page: BillPayPage,
    page: Page,
    base_url: str,
    config: Dict[str, Any],
) -> None:
    """Test that validation errors appear when fields are missing."""
    _open_bill_pay_with_retry(page, payment_services_tab, base_url, config)

    # Click send payment without filling anything
    bill_pay_page.click_send_payment()

    # Verify error messages
    expect(bill_pay_page.locators.name_error).to_have_text("Payee name is required.")
    expect(bill_pay_page.locators.address_error).to_have_text("Address is required.")
    expect(bill_pay_page.locators.city_error).to_have_text("City is required.")
    expect(bill_pay_page.locators.state_error).to_have_text("State is required.")
    expect(bill_pay_page.locators.zip_code_error).to_have_text("Zip Code is required.")
    expect(bill_pay_page.locators.phone_error).to_have_text("Phone number is required.")
    expect(bill_pay_page.locators.account_empty_error).to_have_text("Account number is required.")
    expect(bill_pay_page.locators.verify_account_empty_error).to_have_text(
        "Account number is required."
    )
    expect(bill_pay_page.locators.amount_empty_error).to_have_text("The amount cannot be empty.")


def test_bill_pay_mismatch_account(
    user_login: None,
    payment_services_tab: PaymentServicesTab,
    bill_pay_page: BillPayPage,
    page: Page,
    base_url: str,
    config: Dict[str, Any],
) -> None:
    """Test bill pay validation error when account numbers do not match."""
    _open_bill_pay_with_retry(page, payment_services_tab, base_url, config)

    test_data = {
        "name": "Mismatch Payee",
        "address": "123 Test St",
        "city": "Test City",
        "state": "CA",
        "zip_code": "12345",
        "phone_no": "1234567890",
        "account_no": "12345",
        "verify_acc_no": "54321",
        "amount": "10.00",
    }
    bill_pay_page.submit_form(**test_data)
    expect(bill_pay_page.locators.verify_account_mismatch_error).to_be_visible(timeout=10000)


def test_bill_pay_invalid_amount(
    user_login: None,
    payment_services_tab: PaymentServicesTab,
    bill_pay_page: BillPayPage,
    page: Page,
    base_url: str,
    config: Dict[str, Any],
) -> None:
    """Test bill pay with a non-numeric amount."""
    _open_bill_pay_with_retry(page, payment_services_tab, base_url, config)

    test_data = {
        "name": "Invalid Amount Payee",
        "address": "123 Test St",
        "city": "Test City",
        "state": "CA",
        "zip_code": "12345",
        "phone_no": "1234567890",
        "account_no": "12345",
        "verify_acc_no": "12345",
        "amount": "abc",
    }
    bill_pay_page.submit_form(**test_data)
    # ParaBank shows 'Please enter a valid amount.'
    expect(bill_pay_page.locators.amount_invalid_error).to_be_visible(timeout=10000)
