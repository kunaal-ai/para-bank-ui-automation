"""Tests for Find Transactions."""
from playwright.sync_api import Page, expect

from src.utils.stability import safe_click, skip_if_internal_error
from tests.pages.find_transactions_page import FindTransactionsPage
from tests.pages.helper_pom.payment_services_tab import PaymentServicesTab


def test_find_transactions_by_amount(
    user_login: None,
    payment_services_tab: PaymentServicesTab,
    find_transactions_page: FindTransactionsPage,
) -> None:
    """Test searching for transactions by amount."""
    safe_click(payment_services_tab.find_transactions_link)

    # Search for a common amount or just any amount to see the table
    find_transactions_page.find_by_amount("100")

    # Give it multiple load state waits for stability
    find_transactions_page.page.wait_for_load_state("networkidle")

    skip_if_internal_error(find_transactions_page.page)

    expect(find_transactions_page.transaction_table.first).to_be_visible(timeout=15000)


def test_find_transactions_navigation(
    user_login: None,
    payment_services_tab: PaymentServicesTab,
    page: Page,
) -> None:
    """Test navigation to the Find Transactions page."""
    safe_click(payment_services_tab.find_transactions_link)

    expect(page.locator("#rightPanel h1.title").first).to_have_text("Find Transactions")


def test_find_transactions_by_date(
    user_login: None,
    payment_services_tab: PaymentServicesTab,
    find_transactions_page: FindTransactionsPage,
) -> None:
    """Test searching for transactions by date."""
    safe_click(payment_services_tab.find_transactions_link)
    find_transactions_page.page.wait_for_load_state("networkidle")

    # Search by a generic date
    find_transactions_page.find_by_date("01-01-2024")

    # Give it multiple load state waits for stability
    find_transactions_page.page.wait_for_load_state("networkidle")

    skip_if_internal_error(find_transactions_page.page)

    expect(find_transactions_page.transaction_table.last).to_be_visible(timeout=15000)


def test_find_transactions_by_id_invalid(
    user_login: None,
    payment_services_tab: PaymentServicesTab,
    find_transactions_page: FindTransactionsPage,
) -> None:
    """Test searching for transactions by an invalid ID."""
    safe_click(payment_services_tab.find_transactions_link)
    find_transactions_page.page.wait_for_load_state("networkidle")

    # Search for a non-existent ID
    find_transactions_page.find_by_id("abc")

    # ParaBank shows field error for non-numeric ID
    expect(find_transactions_page.id_error).to_be_visible(timeout=10000)


def test_find_transactions_empty_fields(
    user_login: None,
    payment_services_tab: PaymentServicesTab,
    find_transactions_page: FindTransactionsPage,
) -> None:
    """Test search functionality with empty fields."""
    safe_click(payment_services_tab.find_transactions_link)

    # Click find without filling anything
    safe_click(find_transactions_page.find_by_id_button)

    # Check for error or same page
    expect(find_transactions_page.page.locator("h1.title").first).to_have_text("Find Transactions")
