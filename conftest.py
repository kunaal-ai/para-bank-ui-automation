"""Test configuration and fixtures for ParaBank UI automation."""
import os
import re
import sys
import logging
from pathlib import Path
from typing import Generator, Dict, Any
import pytest
from playwright.sync_api import Page, Browser, BrowserContext, expect

# Import local modules
from tests.pages.home_login_page import HomePage
from tests.pages.bill_pay_page import BillPay
from tests.pages.helper_pom.payment_services_tab import PaymentServicesTab
from src.utils.metrics_pusher import TestMetrics, push_metrics
from config import Config

# Set up logging directory
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)
log_file = log_dir / "test_run.log"

def setup_logging():
    """Configure logging."""
    # Create root logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    
    # Clear existing handlers to avoid duplicate logs
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Console handler
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(formatter)
    console.setLevel(logging.DEBUG)
    
    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    
    # Add handlers
    logger.addHandler(console)
    logger.addHandler(file_handler)
    
    return logging.getLogger("parabank")

# Initialize logger
logger = setup_logging()

# Pytest hooks
def pytest_configure(config):
    """Configure test session."""
    logger.info("=" * 80)
    logger.info("Starting test session")
    logger.info(f"Log level: {logging.getLevelName(logger.getEffectiveLevel())}")
    logger.info("=" * 80)

def pytest_runtest_setup(item):
    """Log test setup."""
    logger.info(f"Starting test: {item.nodeid}")

def pytest_runtest_teardown(item, nextitem):
    """Log test teardown."""
    logger.info(f"Finished test: {item.nodeid}")

def pytest_sessionfinish(session, exitstatus):
    """Log test session completion."""
    logger.info("=" * 80)
    logger.info(f"Test session completed with status: {exitstatus}")
    logger.info("=" * 80)

# Fixtures
@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Set default browser context options."""
    return {
        **browser_context_args,
        "viewport": {
            "width": 1920,
            "height": 1080,
        },
        "record_video_dir": "test-results/videos",
    }

# Global configuration
def pytest_addoption(parser):
    """Add custom command line options."""
    # Environment configuration
    parser.addoption(
        "--env",
        action="store",
        default="dev",
        choices=["dev", "stage", "prod"],
        help="Environment to run tests against (dev, stage, prod)",
    )
    # Session management
    parser.addoption("--no-restore-session", action="store_true", 
                    help="Do not restore the previous session state")
    parser.addoption("--cleanup-session", action="store_true",
                    help="Clean up the session state file after tests")

@pytest.fixture(scope="session")
def env_config(request) -> Config:
    """Fixture to provide environment configuration."""
    env = request.config.getoption("--env", "dev")
    return Config(env=env)

@pytest.fixture(scope="session")
def config(env_config: Config) -> Dict[str, Any]:
    """Global test configuration."""
    return {
        'base_url': env_config.base_url.rstrip('/') + '/',
        'test_results_dir': Path("test-results"),
        'is_ci': bool(os.environ.get("JENKINS_HOME") or os.environ.get("CI")),
        'viewport': {"width": 1280, "height": 800},
        'browser': env_config.browser,
        'headless': env_config.headless,
        'timeout': env_config.timeout
    }

# Browser Configuration
@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args, env_config):
    """Configure browser launch arguments."""
    return {
        **browser_type_launch_args,
        "headless": env_config.get("headless", False),
        "slow_mo": env_config.get("slow_mo", 0)
    }

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args, config):
    """Configure browser context with video recording and viewport settings."""
    return {
        **browser_context_args,
        "viewport": config['viewport'],
        "ignore_https_errors": True,
        "record_video_dir": str(config['test_results_dir'] / "videos"),
        "record_video_size": config['viewport'],
    }

# Test Environment Setup
@pytest.fixture
def context(browser: Browser, browser_context_args: Dict) -> Generator[BrowserContext, None, None]:
    """Create and yield a browser context, then clean up."""
    context = browser.new_context(**browser_context_args)
    yield context
    context.close()

@pytest.fixture
def page(context: BrowserContext, request, config) -> Generator[Page, None, None]:
    """Create a new page and handle test failure screenshots."""
    page = context.new_page()
    pytest.current_test_name = request.node.name
    yield page
    
    if hasattr(pytest, "test_failed") and pytest.test_failed:
        screenshot_path = config['test_results_dir'] / f"screenshot-{pytest.current_test_name}.png"
        page.screenshot(path=str(screenshot_path))
        print(f"Screenshot saved to: {screenshot_path}")

# Page Object Factories
@pytest.fixture(scope="session")
def base_url(env_config) -> str:
    return env_config['base_url']

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
def user_login(page: Page, base_url: str, request, config) -> Generator[None, None, None]:
    """Manage user login session with state persistence."""
    state_file = Path("test-results") / "auth_state.json"
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
