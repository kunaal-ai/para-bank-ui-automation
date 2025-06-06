"""Test configuration and fixtures"""
import os
import re
import pytest
from pathlib import Path
from typing import Generator, Dict
from playwright.sync_api import Page, Browser, BrowserContext, expect
from src.pages.home_login_page import HomePage
from src.pages.bill_pay_page import BillPay
from src.pages.helper_pom.payment_services_tab import PaymentServicesTab
from src.utils.metrics_pusher import TestMetrics, push_metrics

# Configuration
BASE_URL = os.environ.get('BASE_URL', 'https://parabank.parasoft.com/parabank/')
TEST_RESULTS_DIR = Path("test-results")
TEST_RESULTS_DIR.mkdir(exist_ok=True)
IS_CI = bool(os.environ.get('JENKINS_HOME') or os.environ.get('CI'))

# Browser Configuration
@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    """Configure browser launch arguments."""
    return {
        **browser_type_launch_args,
        'headless': IS_CI,
        'slow_mo': 0 if IS_CI else 100,
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

# Browser and Page Fixtures
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

# Page Object Fixtures
@pytest.fixture(scope="session")
def base_url() -> str:
    """Return the base URL for tests."""
    return BASE_URL

@pytest.fixture
def home_page(page: Page, base_url: str) -> HomePage:
    """Return an instance of HomePage with the given page."""
    home_page = HomePage(page)
    home_page.load(base_url)
    return home_page

@pytest.fixture
def bill_pay_page(page: Page) -> BillPay:
    """Return an instance of BillPay with the given page."""
    return BillPay(page)

@pytest.fixture
def payment_services_tab(page: Page) -> PaymentServicesTab:
    """Return an instance of PaymentServicesTab with the given page."""
    return PaymentServicesTab(page)

# Session Management
@pytest.fixture(scope="function")
def user_login(page: Page, base_url: str, request) -> Generator[None, None, None]:
    """Log in once and reuse the session for all tests."""
    state_file = TEST_RESULTS_DIR / "auth_state.json"
    home_page = HomePage(page)
    pytest.current_test_name = request.node.name
    
    # Try to restore session
    if state_file.exists() and not request.config.getoption("--no-restore-session"):
        try:
            home_page.restore_storage_state(str(state_file))
            home_page.load(base_url)
            expect(page).to_have_url(re.compile(r'.*overview\\.htm$'))
            yield
            return
        except Exception:
            print("Failed to restore session. Logging in again...")
    
    # Login if needed
    home_page.load(base_url)
    home_page.user_log_in()
    home_page.save_storage_state(str(state_file))
    
    yield
    
    # Cleanup if requested
    if request.config.getoption("--cleanup-session"):
        try:
            state_file.unlink()
        except Exception as e:
            print(f"Failed to clean up session state: {e}")

# Test Hooks
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Track test failures for screenshots."""
    outcome = yield
    result = outcome.get_result()
    setattr(pytest, "test_failed", result.failed)
    setattr(pytest, "current_test_name", item.nodeid.split("::")[-1])

# Command Line Options
def pytest_addoption(parser):
    """Add custom command line options for pytest."""
    parser.addoption("--no-restore-session", action="store_true", help="Do not restore the previous session state")
    parser.addoption("--cleanup-session", action="store_true", help="Clean up the session state file after tests")

# Metrics
def pytest_configure(config):
    """Initialize metrics when pytest session begins."""
    push_metrics()
    print("Initial metrics pushed to Prometheus Pushgateway")

def pytest_sessionfinish(session, exitstatus):
    """Push final metrics when pytest session ends."""
    push_metrics()
    print("Final metrics pushed to Prometheus Pushgateway")

@pytest.hookimpl(tryfirst=True)
def pytest_runtest_protocol(item, nextitem):
    """Track test metrics for each test."""
    with TestMetrics(item.nodeid):
        return None