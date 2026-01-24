"""Tests for Updating Contact Info."""
import pytest
from playwright.sync_api import Page, expect

from tests.pages.helper_pom.payment_services_tab import PaymentServicesTab
from tests.pages.update_contact_info_page import UpdateContactInfoPage


@pytest.mark.usefixtures("user_login")
def test_update_zip_code_successful(
    page: Page,
    update_contact_info_page: UpdateContactInfoPage,
    payment_services_tab: PaymentServicesTab,
) -> None:
    """Verify that the zip code can be updated successfully."""
    # Navigate to Update Contact Info
    payment_services_tab.update_contact_info_link.click()

    # Update Zip Code
    new_zip = "54321"
    update_contact_info_page.update_zip_code(new_zip)

    # Verify success
    expect(page.locator("#rightPanel").get_by_text("Profile Updated").first).to_be_visible()
    expect(
        page.locator("text=Your updated address and phone number have been added to the system.")
    ).to_be_visible()
