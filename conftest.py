"""Test configuration and fixtures"""
import os
import pytest
from typing import Generator
from playwright.sync_api import Page, expect
from pages.home_login_page import HomePage
from pages.bill_pay_page import BillPay
from pages.helper_pom.payment_services_tab import PaymentServicesTab
from metrics_pusher import TestMetrics, push_metrics

# Get base URL from environment or use default
BASE_URL = os.environ.get('BASE_URL', 'https://parabank.parasoft.com/parabank/')



@pytest.fixture(scope="session")
def base_url() -> str:
    """Return the base URL for tests."""
    return BASE_URL

@pytest.fixture
def home_page(page: Page, base_url: str) -> HomePage:
    """Return an instance of HomePage with the given page."""
    home_page = HomePage(page)
    # Load the page with the base URL
    home_page.load(base_url)
    return home_page

@pytest.fixture(scope="function")
def user_login(page: Page, base_url: str, request) -> Generator[None, None, None]:
    """Log in once and reuse the session for all tests.
    
    This fixture will save the authentication state after the first login
    and restore it for subsequent tests.
    """
    state_file = "auth_state.json"
    home_page = HomePage(page)
    
    # Try to restore the session if it exists
    if os.path.exists(state_file) and not request.config.getoption("--no-restore-session"):
        print("Restoring session from state file...")
        home_page.restore_storage_state(state_file)
        home_page.load(base_url)
        
        # Verify we're still logged in
        try:
            expect(page).to_have_url(re.compile(r'.*overview\.htm$'))
            print("Successfully restored session")
            yield
            return
        except Exception as e:
            print(f"Failed to restore session: {e}. Logging in again...")
    
    # If we get here, we need to log in
    home_page.load(base_url)
    home_page.user_log_in()
    
    # Save the authentication state for future tests
    home_page.save_storage_state(state_file)
    print("Saved new session state")
    
    yield
    
    # Clean up after test if needed
    if request.config.getoption("--cleanup-session"):
        try:
            os.remove(state_file)
            print("Cleaned up session state file")
        except Exception as e:
            print(f"Failed to clean up session state: {e}")

@pytest.fixture
def bill_pay_page(page: Page) -> BillPay:
    """Return an instance of BillPay with the given page."""
    return BillPay(page)

@pytest.fixture
def payment_services_tab(page: Page) -> PaymentServicesTab:
    """Return an instance of PaymentServicesTab with the given page."""
    return PaymentServicesTab(page)

# Add command line options
def pytest_addoption(parser):
    """Add custom command line options for pytest."""
    parser.addoption(
        "--no-restore-session",
        action="store_true",
        default=False,
        help="Do not restore the previous session state"
    )
    parser.addoption(
        "--cleanup-session",
        action="store_true",
        default=False,
        help="Clean up the session state file after tests"
    )

# Initialize metrics when pytest session begins
def pytest_configure(config):
    # Push initial metrics to the Pushgateway
    push_metrics()
    print("Initial metrics pushed to Prometheus Pushgateway")
    
# Push final metrics when pytest session ends
def pytest_sessionfinish(session, exitstatus):
    push_metrics()
    print("Final metrics pushed to Prometheus Pushgateway")

# Track test metrics for each test
@pytest.hookimpl(tryfirst=True)
def pytest_runtest_protocol(item, nextitem):
    test_name = item.nodeid
    with TestMetrics(test_name):
        return None  # Let pytest handle the test execution

# Track test outcomes
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    
    # We only want to track the final test outcome
    if report.when == 'call':
        test_name = item.nodeid
        # TestMetrics will automatically track passes/failures