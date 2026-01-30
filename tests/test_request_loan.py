"""Tests for the Request Loan functionality."""
import pytest
from playwright.sync_api import Page, expect

from tests.pages.helper_pom.payment_services_tab import PaymentServicesTab
from tests.pages.request_loan_page import RequestLoanPage


@pytest.mark.usefixtures("user_login")
class TestRequestLoan:
    """Class to group tests for request loan."""

    @pytest.mark.flaky
    def test_request_loan_denied_insufficient_funds(
        self,
        page: Page,
        request_loan_page: RequestLoanPage,
        payment_services_tab: PaymentServicesTab,
    ) -> None:
        """Verify that a loan is denied when there are insufficient funds for down payment."""
        # Navigate to Request Loan
        payment_services_tab.request_loan_link.click()

        # Apply for a loan with a high down payment
        request_loan_page.apply_for_loan(amount="10000", down_payment="5000")

        # Verify it is denied
        assert request_loan_page.is_loan_denied()
        expect(
            page.locator("text=You do not have sufficient funds for the given down payment.")
        ).to_be_visible()

    @pytest.mark.flaky
    def test_request_loan_navigation(self, payment_services_tab: PaymentServicesTab) -> None:
        """Verify navigation to the request loan page."""
        payment_services_tab.request_loan_link.click()
        expect(payment_services_tab.page.locator("#rightPanel h1.title").first).to_have_text(
            "Apply for a Loan"
        )

    @pytest.mark.flaky
    def test_request_loan_empty_fields(
        self,
        request_loan_page: RequestLoanPage,
        payment_services_tab: PaymentServicesTab,
    ) -> None:
        """Verify validation when loan fields are empty."""
        payment_services_tab.request_loan_link.click()

        # Click Apply without filling anything
        request_loan_page.apply_button.click()

        # Should stay on page or show error
        expect(request_loan_page.page.locator("h1.title").first).to_have_text("Apply for a Loan")

    @pytest.mark.flaky
    def test_request_loan_form_elements(
        self,
        request_loan_page: RequestLoanPage,
        payment_services_tab: PaymentServicesTab,
    ) -> None:
        """Verify presence of all elements in the loan request form."""
        payment_services_tab.request_loan_link.click()

        expect(request_loan_page.amount_input).to_be_visible()
        expect(request_loan_page.down_payment_input).to_be_visible()
        expect(request_loan_page.from_account_dropdown).to_be_visible()
        expect(request_loan_page.apply_button).to_be_visible()
