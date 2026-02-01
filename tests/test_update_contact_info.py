"""Tests for Updating Contact Info."""
import logging

import pytest
from playwright.sync_api import Page, expect

from src.utils.stability import handle_internal_error
from tests.pages.helper_pom.payment_services_tab import PaymentServicesTab
from tests.pages.update_contact_info_page import UpdateContactInfoPage

logger = logging.getLogger("parabank")
pytestmark = pytest.mark.usefixtures("user_login")


@pytest.mark.flaky
def test_update_zip_code_successful(
    page: Page,
    update_contact_info_page: UpdateContactInfoPage,
    payment_services_tab: PaymentServicesTab,
    user_factory,
) -> None:
    """Verify that the zip code can be updated successfully."""
    # Navigate to Update Contact Info
    payment_services_tab.navigate_to("update_contact")

    # Update Zip Code using dynamic data
    new_user = user_factory.create_user()
    update_contact_info_page.update_zip_code(new_user.zip_code)

    # Wait for page navigation or success indicator
    page.wait_for_timeout(1000)  # Allow JS hydration
    handle_internal_error(page, requires_login=True)

    # Use robust CSS locator for title
    success_title = page.locator("#rightPanel .title")
    expect(success_title).to_contain_text("Profile Updated", timeout=15000)

    expect(
        page.locator("#rightPanel p")
        .get_by_text("Your updated address and phone number have been added to the system.")
        .first
    ).to_be_visible(timeout=10000)


@pytest.mark.flaky
def test_update_contact_info_validation(
    page: Page,
    update_contact_info_page: UpdateContactInfoPage,
    payment_services_tab: PaymentServicesTab,
) -> None:
    """Verify validation when required contact fields are cleared."""
    payment_services_tab.navigate_to("update_contact")

    # Clear First Name
    update_contact_info_page.first_name_input.clear()
    update_contact_info_page.update_button.click()

    # Check for error
    expect(page.locator("#firstName-error")).to_be_visible(timeout=10000)


@pytest.mark.flaky
def test_update_full_profile(
    update_contact_info_page: UpdateContactInfoPage,
    payment_services_tab: PaymentServicesTab,
    page: Page,
    user_factory,
) -> None:
    """Verify updating all profile fields."""
    payment_services_tab.navigate_to("update_contact")

    # Generate dynamic user data for update
    updated_user = user_factory.create_user()

    update_contact_info_page.first_name_input.fill(updated_user.first_name)
    update_contact_info_page.last_name_input.fill(updated_user.last_name)
    update_contact_info_page.address_input.fill(updated_user.address)
    update_contact_info_page.city_input.fill(updated_user.city)
    update_contact_info_page.state_input.fill(updated_user.state)
    update_contact_info_page.zip_code_input.fill(updated_user.zip_code)
    update_contact_info_page.phone_input.fill(updated_user.phone)

    update_contact_info_page.update_button.click()

    # Wait for page navigation or success indicator
    page.wait_for_timeout(1000)  # Allow JS hydration
    handle_internal_error(page, requires_login=True)

    # Use robust CSS locator for title
    success_title = page.locator("#rightPanel .title")
    expect(success_title).to_contain_text("Profile Updated", timeout=15000)

    expect(
        page.locator("#rightPanel p")
        .get_by_text("Your updated address and phone number have been added to the system.")
        .first
    ).to_be_visible(timeout=10000)
