import logging

from playwright.sync_api import Page, expect

from tests.data.user_factory import UserFactory
from tests.pages.account_overview_page import AccountOverviewPage
from tests.pages.bill_pay_page import BillPayPage
from tests.pages.find_transactions_page import FindTransactionsPage
from tests.pages.helper_pom.payment_services_tab import PaymentServicesTab
from tests.pages.home_login_page import HomePage
from tests.pages.open_account_page import OpenAccountPage
from tests.pages.register_page import RegisterPage
from tests.pages.request_loan_page import RequestLoanPage
from tests.pages.transfer_funds_page import TransferFundsPage
from tests.pages.update_contact_info_page import UpdateContactInfoPage

logger = logging.getLogger("parabank")


def test_e2e_happy_path_workflow(
    page: Page, base_url: str, user_factory: UserFactory, payment_services_tab: PaymentServicesTab
) -> None:
    """
    End-to-End Happy Path Test covering:
    1. Registration
    2. Open New Account
    3. Account Overview (verification)
    4. Transfer Funds
    5. Find Transactions
    6. Bill Pay
    7. Request Loan
    8. Update Contact Info
    9. Logout
    """
    logger.info("Starting E2E Happy Path Workflow")

    # --- 1. Registration ---
    home_page = HomePage(page)
    home_page.load(base_url)

    # Navigate to Register
    page.get_by_role("link", name="Register").click()

    register_page = RegisterPage(page)
    user = user_factory.create_user()
    user_data = user.to_dict()

    logger.info(f"Registering user: {user.username}")
    register_page.register(user_data)
    register_page.verify_registration_success(user.username, user.password)

    # --- 2. Open New Account ---
    logger.info("Opening a new Savings account")
    page.wait_for_load_state("networkidle")
    payment_services_tab.open_new_account_link.click()

    open_account_page = OpenAccountPage(page)

    # Wait for the page to be fully stable
    page.wait_for_load_state("domcontentloaded")

    # Wait for the select to be populated (it takes a moment to fetch existing accounts)
    try:
        page.wait_for_selector("select#fromAccountId option", timeout=30000)
    except Exception:
        logger.warning("Timeout waiting for accounts dropdown. Retrying navigation...")
        payment_services_tab.open_new_account_link.click()
        page.wait_for_selector("select#fromAccountId option", timeout=30000)

    # Open a SAVINGS account using the first available account as source
    open_account_page.open_new_account(account_type="SAVINGS", from_account_index=0)

    # Verify account opened
    try:
        expect(open_account_page.account_opened_heading).to_be_visible(timeout=30000)
    except Exception as e:
        logger.error(f"Account opening failed. Title: {page.title()}")
        # Check if we got an internal error
        if "Internal Error" in page.content():
            logger.error("Encountered ParaBank Internal Error during Open Account.")
        raise e

    # Extract new account ID from the link "Your new account # is 13566."
    new_account_id_locator = page.locator("#newAccountId")
    expect(new_account_id_locator).to_be_visible()
    new_account_id = new_account_id_locator.inner_text()
    logger.info(f"New Account Opened: {new_account_id}")

    # --- 3. Account Overview ---
    logger.info("Verifying Account Overview")
    payment_services_tab.accounts_overview_link.click()
    account_overview_page = AccountOverviewPage(page)
    account_overview_page.wait_for_data()

    # Gather all account numbers
    account_links = page.locator("#accountTable tbody tr td:first-child a").all()
    account_numbers = [link.inner_text() for link in account_links]
    logger.info(f"Found accounts: {account_numbers}")

    assert len(account_numbers) >= 2, "Should have at least 2 accounts now"
    assert new_account_id in account_numbers, "New account ID should be listed in overview"

    from_account = account_numbers[0]  # Usually the checking account created on reg
    to_account = new_account_id

    # --- 4. Transfer Funds ---
    logger.info(f"Transferring funds from {from_account} to {to_account}")
    payment_services_tab.transfer_funds_link.click()
    transfer_page = TransferFundsPage(page)

    # Transfer $100
    transfer_amount = "100.00"
    # Delay slightly to ensure options are loaded (handled in POM but good to be safe)
    page.wait_for_timeout(1000)
    transfer_page.submit_transfer(
        amount=transfer_amount, from_account=from_account, to_account=to_account
    )
    transfer_page.verify_success()
    expect(page.get_by_text(f"${transfer_amount} has been transferred")).to_be_visible()

    # --- 5. Find Transactions ---
    logger.info("Finding the transfer transaction")
    payment_services_tab.find_transactions_link.click()
    find_trans_page = FindTransactionsPage(page)

    # We look for the transaction in the 'from' account
    page.locator("#accountId").select_option(label=from_account)

    # Search by amount
    find_trans_page.find_by_amount(transfer_amount)
    find_trans_page.wait_for_results()

    # Verify transaction table contains the amount
    expect(page.locator("#transactionTable")).to_contain_text(f"${transfer_amount}")

    # --- 6. Bill Pay ---
    logger.info("Paying a bill")
    payment_services_tab.bill_pay_link.click()
    bill_pay_page = BillPayPage(page)

    bill_pay_data = {
        "name": "Electric Company",
        "address": "123 Power Grid",
        "city": "Volttown",
        "state": "CA",
        "zip_code": "90210",
        "phone_no": "555-0001",
        "account_no": "987654321",
        "verify_acc_no": "987654321",
        "amount": "50.00",
    }

    # We might need to select the From Account if it's a dropdown, but BillPayPage.submit_form
    # currently doesn't take 'from_account' argument, it uses default or whatever is selected.
    # The POM implementation of submit_form just fills interactions.
    # Let's check if there is a 'from account' dropdown on Bill Pay page.
    # Even if there is, usually it defaults to the first one.

    bill_pay_page.submit_form(**bill_pay_data)
    expect(page.locator("#billpayResult h1.title")).to_have_text("Bill Payment Complete")
    expect(page.get_by_text(f"Bill Payment to {bill_pay_data['name']}")).to_be_visible()

    # --- 7. Request Loan ---
    logger.info("Requesting a loan")
    payment_services_tab.request_loan_link.click()
    request_loan_page = RequestLoanPage(page)

    # Request a small loan that is likely to be approved
    loan_amount = "100.00"
    down_payment = "10.00"
    # Select the first account as the down payment account

    request_loan_page.apply_for_loan(
        amount=loan_amount, down_payment=down_payment, from_account=from_account
    )

    # Verify result - sometimes it's approved, sometimes denied depending on backend logic.
    # We just want to ensure the process completes.
    # checking for "Loan Request Processed" title which appears in both cases
    expect(page.locator("#loanRequestApproved h1.title, .title")).to_contain_text(
        "Loan Request Processed"
    )

    # --- 8. Update Contact Info ---
    logger.info("Updating Contact Info")
    payment_services_tab.update_contact_info_link.click()
    update_profile_page = UpdateContactInfoPage(page)

    # Wait for form to load current values (sometimes takes a bit)
    expect(page.locator("input[name='customer.firstName']")).not_to_be_empty(timeout=10000)

    new_phone = "555-999-8888"
    update_profile_page.update_phone_number(new_phone)

    expect(page.get_by_text("Profile Updated")).to_be_visible()

    # --- 9. Logout ---
    logger.info("Logging out")
    page.get_by_role("link", name="Log Out").click()

    # Verify we are on login screen
    expect(page.locator("input[name='username']")).to_be_visible()

    logger.info("E2E Happy Path Test Completed Successfully")
