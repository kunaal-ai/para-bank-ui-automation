"""Tests for Account Overview."""
from playwright.sync_api import Page, expect

from tests.pages.account_overview_page import AccountOverviewPage


def test_account_overview_details(
    user_login: None,
    account_overview_page: AccountOverviewPage,
) -> None:
    """Test that account overview displays account details correctly."""
    account_overview_page.wait_for_data()

    expect(account_overview_page.title).to_have_text("Accounts Overview")

    account_num = account_overview_page.get_first_account_number()
    balance = account_overview_page.get_first_account_balance()

    assert account_num.isdigit(), f"Expected account number to be digits, got {account_num}"
    assert "$" in balance, f"Expected balance to contain $, got {balance}"


def test_navigate_to_account_details(
    user_login: None,
    account_overview_page: AccountOverviewPage,
    page: Page,
) -> None:
    """Test navigation from overview to account details."""
    account_overview_page.wait_for_data()
    account_num = account_overview_page.get_first_account_number()

    account_overview_page.click_first_account()

    # Verify we are on the Account Details page
    expect(page.locator("#rightPanel h1.title").first).to_have_text("Account Details")
    expect(page.locator("#accountId")).to_have_text(account_num)


def test_account_activity_filtering(
    user_login: None,
    account_overview_page: AccountOverviewPage,
    page: Page,
) -> None:
    """Test filtering account activity on the Account Details page."""
    account_overview_page.wait_for_data()
    account_overview_page.click_first_account()

    # Filter by month 'All' and type 'All'
    page.select_option("#month", "All")
    page.select_option("#transactionType", "All")
    page.click("input[value='Go']")

    # ParaBank can show the table and/or a "No transactions found." hint.
    table = page.locator("#transactionTable")
    no_results = page.get_by_text("No transactions found.")
    page.wait_for_timeout(500)
    assert table.is_visible() or no_results.is_visible(), (
        "Expected either a visible transaction table or "
        "'No transactions found.' message after filtering."
    )


def test_total_balance_presence(
    user_login: None,
    account_overview_page: AccountOverviewPage,
) -> None:
    """Test that the Total balance row is present in the overview."""
    account_overview_page.wait_for_data()
    total_label = account_overview_page.page.locator("td:has-text('Total')")
    expect(total_label).to_be_visible()
