"""Test configuration and fixtures for ParaBank UI automation."""

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

# Global configuration
CONFIG = {
    'base_url': os.environ.get("BASE_URL", "https://parabank.parasoft.com/parabank/"),
    'test_results_dir': Path("test-results"),
    'is_ci': bool(os.environ.get("JENKINS_HOME") or os.environ.get("CI")),
    'viewport': {"width": 1280, "height": 800}
}
CONFIG['test_results_dir'].mkdir(exist_ok=True)

def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption("--no-restore-session", action="store_true", 
                    help="Do not restore the previous session state")
    parser.addoption("--cleanup-session", action="store_true",
                    help="Clean up the session state file after tests")

# Browser Configuration
@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    """Configure browser launch arguments."""
    return {
        **browser_type_launch_args,
        "headless": CONFIG['is_ci'],
        "slow_mo": 0 if CONFIG['is_ci'] else 100,
    }

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configure browser context with video recording and viewport settings."""
    return {
        **browser_context_args,
        "viewport": CONFIG['viewport'],
        "ignore_https_errors": True,
        "record_video_dir": str(CONFIG['test_results_dir'] / "videos"),
        "record_video_size": CONFIG['viewport'],
    }

# Test Environment Setup
@pytest.fixture
def context(browser: Browser, browser_context_args: Dict) -> Generator[BrowserContext, None, None]:
    """Create and yield a browser context, then clean up."""
    context = browser.new_context(**browser_context_args)
    yield context
    context.close()

@pytest.fixture
def page(context: BrowserContext, request) -> Generator[Page, None, None]:
    """Create a new page and handle test failure screenshots."""
    page = context.new_page()
    pytest.current_test_name = request.node.name
    yield page
    
    if hasattr(pytest, "test_failed") and pytest.test_failed:
        screenshot_path = CONFIG['test_results_dir'] / f"screenshot-{pytest.current_test_name}.png"
        page.screenshot(path=str(screenshot_path))
        print(f"Screenshot saved to: {screenshot_path}")

# Page Object Factories
@pytest.fixture(scope="session")
def base_url() -> str:
    return CONFIG['base_url']

@pytest.fixture
def home_page(page: Page, base_url: str) -> HomePage:
    """Initialize and return the home page."""
    home_page = HomePage(page)
    home_page.load(base_url)
    return home_page

@pytest.fixture
def bill_pay_page(page: Page) -> BillPay:
    return BillPay(page)

@pytest.fixture
def payment_services_tab(page: Page) -> PaymentServicesTab:
    return PaymentServicesTab(page)

# Session Management
@pytest.fixture(scope="function")
def user_login(page: Page, base_url: str, request) -> Generator[None, None, None]:
    """Manage user login session with state persistence."""
    state_file = CONFIG['test_results_dir'] / "auth_state.json"
    home_page = HomePage(page)
    
    # Try to restore session if possible
    if state_file.exists() and not request.config.getoption("--no-restore-session"):
        try:
            home_page.restore_storage_state(str(state_file))
            home_page.load(base_url)
            expect(page).to_have_url(re.compile(r".*overview\\.htm$"))
            yield
            return
        except Exception:
            print("Failed to restore session. Logging in again...")
    
    # Perform login and save state
    home_page.load(base_url)
    home_page.user_log_in()
    home_page.save_storage_state(str(state_file))
    
    yield
    
    # Cleanup if requested
    if request.config.getoption("--cleanup-session") and state_file.exists():
        state_file.unlink(missing_ok=True)

# Test Hooks
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Track test failures for screenshots."""
    outcome = yield
    result = outcome.get_result()
    setattr(pytest, "test_failed", result.failed)
    setattr(pytest, "current_test_name", item.nodeid.split("::")[-1])

# Metrics Integration
def pytest_configure(config):
    """Initialize metrics at session start."""
    push_metrics()
    print("Initial metrics pushed to Prometheus Pushgateway")

def pytest_sessionfinish(session, exitstatus):
    """Push final metrics at session end."""
    push_metrics()
    print("Final metrics pushed to Prometheus Pushgateway")

@pytest.hookimpl(tryfirst=True)
def pytest_runtest_protocol(item, nextitem):
    """Track test metrics for each test."""
    with TestMetrics(item.nodeid):
        return None
