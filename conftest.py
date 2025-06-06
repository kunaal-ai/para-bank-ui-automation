"""Test configuration and fixtures"""
import os
import re
import pytest
import json
from typing import Generator, Dict, Any
from pathlib import Path
from playwright.sync_api import Page, Browser, BrowserContext, expect, Playwright
from pages.home_login_page import HomePage
from pages.bill_pay_page import BillPay
from pages.helper_pom.payment_services_tab import PaymentServicesTab
from metrics_pusher import TestMetrics, push_metrics

# Get base URL from environment or use default
BASE_URL = os.environ.get('BASE_URL', 'https://parabank.parasoft.com/parabank/')

# Configure test output directories
TEST_RESULTS_DIR = Path("test-results")
TEST_RESULTS_DIR.mkdir(exist_ok=True)

# Check if running in CI environment
IS_CI = bool(os.environ.get('JENKINS_HOME') or os.environ.get('CI'))

@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    """Configure browser launch arguments."""
    return {
        **browser_type_launch_args,
        'headless': IS_CI,  # Use headless mode in CI
        'slow_mo': 0 if IS_CI else 100,  # No slowdown in CI
    }

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configure browser context arguments."""
    return {
        **browser_context_args,
        'viewport': {'width': 1280, 'height': 800},
        'ignore_https_errors': True,
        'record_video_dir': str(TEST_RESULTS_DIR / 'videos'),
        'record_video_size': {'width': 1280, 'height': 800},
    }

@pytest.fixture
def context(browser: Browser, browser_context_args: Dict) -> Generator[BrowserContext, None, None]:
    """Create a new browser context for each test."""
    context = browser.new_context(**browser_context_args)
    yield context
    context.close()

@pytest.fixture
def page(context: BrowserContext) -> Generator[Page, None, None]:
    """Create a new page for each test."""
    page = context.new_page()
    yield page
    
    # Take screenshot on test failure
    if hasattr(pytest, "test_failed") and pytest.test_failed:
        screenshot_path = TEST_RESULTS_DIR / f"screenshot-{pytest.current_test_name}.png"
        page.screenshot(path=str(screenshot_path))
        print(f"Screenshot saved to: {screenshot_path}")

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
    """Log in once and reuse the session for all tests."""
    state_file = TEST_RESULTS_DIR / "auth_state.json"
    home_page = HomePage(page)
    
    # Set test name for better error reporting
    pytest.current_test_name = request.node.name
    
    # Try to restore the session if it exists
    if state_file.exists() and not request.config.getoption("--no-restore-session"):
        print("Restoring session from state file...")
        home_page.restore_storage_state(str(state_file))
        home_page.load(base_url)
        
        # Verify we're still logged in
        try:
            expect(page).to_have_url(re.compile(r'.*overview\\.htm$'))
            print("Successfully restored session")
            yield
            return
        except Exception as e:
            print(f"Failed to restore session: {e}. Logging in again...")
    
    # If we get here, we need to log in
    home_page.load(base_url)
    home_page.user_log_in()
    
    # Save the authentication state for future tests
    home_page.save_storage_state(str(state_file))
    print("Saved new session state")
    
    yield
    
    # Clean up after test if needed
    if request.config.getoption("--cleanup-session"):
        try:
            state_file.unlink()
            print("Cleaned up session state file")
        except Exception as e:
            print(f"Failed to clean up session state: {e}")

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Track test failures for screenshots."""
    outcome = yield
    result = outcome.get_result()
    setattr(pytest, "test_failed", result.failed)
    setattr(pytest, "current_test_name", item.nodeid.split("::")[-1])

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