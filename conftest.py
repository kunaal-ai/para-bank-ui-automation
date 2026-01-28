"""Test configuration and fixtures for ParaBank UI automation."""
import logging
import sys
from pathlib import Path
from typing import Any, Dict, Generator, Optional

import pytest
from _pytest.config import Config as PytestConfig
from _pytest.config.argparsing import Parser
from _pytest.fixtures import FixtureRequest
from _pytest.nodes import Item
from _pytest.runner import CallInfo
from playwright.sync_api import Browser, BrowserContext, Page, expect

from config import Config
from src.utils.metrics_pusher import ExecutionMetrics
from tests.pages.account_overview_page import AccountOverviewPage
from tests.pages.bill_pay_page import BillPayPage
from tests.pages.find_transactions_page import FindTransactionsPage
from tests.pages.helper_pom.payment_services_tab import PaymentServicesTab
from tests.pages.home_login_page import HomePage
from tests.pages.open_account_page import OpenAccountPage
from tests.pages.request_loan_page import RequestLoanPage
from tests.pages.update_contact_info_page import UpdateContactInfoPage

# Set up logging directory
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)
log_file = log_dir / "test_run.log"


def setup_logging() -> logging.Logger:
    """Configure logging.

    Returns:
        logging.Logger: Configured logger instance
    """
    # Create root logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Clear existing handlers to avoid duplicate logs
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(formatter)
    console.setLevel(logging.DEBUG)

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
def pytest_configure(config: PytestConfig) -> None:
    """Pytest configuration hook.

    Args:
        config: Pytest config object
    """
    logger = logging.getLogger("parabank")
    logger.info("=" * 80)
    logger.info("Starting test session")
    logger.info(f"Log level: {logging.getLevelName(logger.getEffectiveLevel())}")
    logger.info("=" * 80)


def pytest_runtest_setup(item: Item) -> None:
    """Log test setup.

    Args:
        item: Pytest test item
    """
    logger.info(f"Starting test: {item.nodeid}")


def pytest_runtest_teardown(item: Item, nextitem: Optional[Item]) -> None:
    """Log test teardown.

    Args:
        item: Current test item
        nextitem: Next test item, if any
    """
    logger.info(f"Finished test: {item.nodeid}")


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    """Log test session completion and push metrics.

    Args:
        session: Pytest session object
        exitstatus: Exit status code
    """
    session_logger = logging.getLogger("parabank")
    session_logger.info("=" * 80)
    session_logger.info(f"Test session completed with status: {exitstatus}")
    session_logger.info("=" * 80)
    # Metrics are pushed per-test in ExecutionMetrics context manager


# Fixtures
@pytest.fixture(scope="session")
def browser_context_args(
    browser_context_args: Dict[str, Any], config: Dict[str, Any], auth_state: Path
) -> Dict[str, Any]:
    """Unified browser context configuration with session reuse."""
    return {
        **browser_context_args,
        "viewport": config["viewport"],
        "ignore_https_errors": True,
        "record_video_dir": str(config["test_results_dir"] / "videos"),
        "record_video_size": config["viewport"],
        "storage_state": str(auth_state) if auth_state.exists() else None,
    }


# Global configuration
def pytest_addoption(parser: Parser) -> None:
    """Add custom command line options.

    Args:
        parser: Pytest argument parser
    """
    parser.addoption(
        "--env",
        action="store",
        default="dev",
        choices=["dev", "stage", "prod"],
        help="Environment to run tests against (dev, stage, prod)",
    )
    # Note: --browser and --headed/--headless are provided by pytest-playwright plugin
    # Browser selection should be done via:
    # 1. Environment config files (config/{env}.json) - recommended
    # 2. pytest-playwright options: --browser=chromium|firefox|webkit


@pytest.fixture(scope="session")
def env_config(request: FixtureRequest) -> Config:
    """Fixture to provide environment configuration.

    Args:
        request: Pytest fixture request object

    Returns:
        Config: Configuration object for the test environment
    """
    env = request.config.getoption("--env")
    return Config(env)


@pytest.fixture(scope="session")
def config(env_config: Config) -> Dict[str, Any]:
    """Global test configuration.

    Args:
        env_config: Environment configuration

    Returns:
        Dictionary with test configuration
    """
    # Setup test results directory
    test_results_dir = Path("test-results")
    test_results_dir.mkdir(exist_ok=True)

    return {
        "browser": env_config.browser,
        "headless": env_config.headless,
        "base_url": env_config.base_url,
        "viewport": {"width": 1920, "height": 1080},
        "test_results_dir": test_results_dir,
        "test_user": env_config.users["valid"],
    }


# Browser Configuration
@pytest.fixture(scope="session")
def browser_type_launch_args(
    browser_type_launch_args: Dict[str, Any], env_config: Config
) -> Dict[str, Any]:
    """Configure browser launch arguments.

    Args:
        browser_type_launch_args: Default browser launch arguments
        env_config: Environment configuration

    Returns:
        Dictionary of browser launch arguments
    """
    # Add any additional browser launch arguments here
    browser_type_launch_args.update(
        {
            "headless": env_config.headless,
        }
    )
    # Add slow_mo if it exists in config
    if hasattr(env_config, "slow_mo") and env_config.slow_mo:
        browser_type_launch_args["slow_mo"] = env_config.slow_mo
    return browser_type_launch_args


# Test Environment Setup
@pytest.fixture
def context(
    browser: Browser, browser_context_args: Dict[str, Any]
) -> Generator[BrowserContext, None, None]:
    """Create and yield a browser context, then clean up.

    Args:
        browser: Playwright browser instance
        browser_context_args: Browser context arguments

    Yields:
        BrowserContext: Configured browser context
    """
    context = browser.new_context(**browser_context_args)
    yield context
    context.close()


@pytest.fixture
def page(
    context: BrowserContext, request: FixtureRequest, config: Dict[str, Any]
) -> Generator[Page, None, None]:
    """Create a new page and handle test failure screenshots.

    Args:
        context: Browser context
        request: Pytest fixture request
        config: Test configuration

    Yields:
        Page: New browser page
    """
    page = context.new_page()
    yield page

    # Take screenshot on test failure
    if hasattr(request.node, "rep_call") and request.node.rep_call.failed:
        screenshot_dir = config["test_results_dir"] / "screenshots"
        screenshot_dir.mkdir(exist_ok=True)
        test_name = request.node.name.replace("[", "_").replace("]", "_")
        screenshot_path = screenshot_dir / f"{test_name}.png"
        page.screenshot(path=str(screenshot_path))
        print(f"Screenshot saved to: {screenshot_path}")


# Page Object Factories
@pytest.fixture(scope="session")
def base_url(env_config: Config) -> str:
    """Get the base URL for the test environment.

    Args:
        env_config: Environment configuration

    Returns:
        Base URL string
    """
    return str(env_config.base_url)


@pytest.fixture
def home_page(page: Page, base_url: str) -> HomePage:
    """Initialize and return the home page.

    Args:
        page: Browser page
        base_url: Base URL of the application

    Returns:
        Initialized HomePage instance
    """
    home_page = HomePage(page)
    home_page.load(base_url)
    return home_page


@pytest.fixture
def bill_pay_page(page: Page) -> BillPayPage:
    """Create a BillPayPage actions object.

    Args:
        page: Browser page

    Returns:
        Initialized BillPayPage instance
    """
    return BillPayPage(page)


@pytest.fixture
def payment_services_tab(page: Page) -> PaymentServicesTab:
    """Create a PaymentServicesTab page object.

    Args:
        page: Browser page

    Returns:
        Initialized PaymentServicesTab instance
    """
    return PaymentServicesTab(page)


@pytest.fixture
def open_account_page(page: Page) -> OpenAccountPage:
    """Create an OpenAccountPage page object.

    Args:
        page: Browser page

    Returns:
        Initialized OpenAccountPage instance
    """
    return OpenAccountPage(page)


@pytest.fixture
def request_loan_page(page: Page) -> RequestLoanPage:
    """Create a RequestLoanPage page object.

    Args:
        page: Browser page

    Returns:
        Initialized RequestLoanPage instance
    """
    return RequestLoanPage(page)


@pytest.fixture
def update_contact_info_page(page: Page) -> UpdateContactInfoPage:
    """Create an UpdateContactInfoPage page object.

    Args:
        page: Browser page

    Returns:
        Initialized UpdateContactInfoPage instance
    """
    return UpdateContactInfoPage(page)


@pytest.fixture
def account_overview_page(page: Page) -> AccountOverviewPage:
    """Create an AccountOverviewPage page object.

    Args:
        page: Browser page

    Returns:
        Initialized AccountOverviewPage instance
    """
    return AccountOverviewPage(page)


@pytest.fixture
def find_transactions_page(page: Page) -> FindTransactionsPage:
    """Create a FindTransactionsPage page object.

    Args:
        page: Browser page

    Returns:
        Initialized FindTransactionsPage instance
    """
    return FindTransactionsPage(page)


# Session Management
@pytest.fixture(scope="session")
def auth_state(browser: Browser, config: Dict[str, Any], base_url: str) -> Path:
    """Perform login once at the start of the session and return the state file path."""
    state_file = Path("test-results/state.json")
    state_file.parent.mkdir(exist_ok=True)

    context = browser.new_context()
    page = context.new_page()

    test_user = config["test_user"]
    page.goto(base_url)
    page.fill("input[name='username']", test_user["username"])
    page.fill("input[name='password']", test_user["password"])
    page.click("input[value='Log In']")

    # Wait for login to complete
    expect(page.locator("#leftPanel p.smallText")).to_be_visible(timeout=10000)

    context.storage_state(path=str(state_file))
    context.close()
    return state_file


@pytest.fixture
def user_login(page: Page, auth_state: Path, base_url: str) -> None:
    """Apply the pre-authenticated state to the current page. This is extremely fast."""
    # The browser context is already created by playwright fixture.
    # We navigate directly to the logged-in area.
    page.goto(f"{base_url}/overview.htm")

    # If for some reason we aren't logged in, redirect to login (safeguard)
    if "Accounts Overview" not in page.title():
        page.goto(base_url)


# Test Hooks
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item: Item, call: CallInfo[None]) -> Generator[Any, None, None]:
    """Track test failures for screenshots."""
    outcome: Any = yield
    result: Any = outcome.get_result()
    # Capture the outcome of the test (passed, failed, skipped)
    if result.skipped:
        item.status = "skipped"
    elif result.failed:
        item.status = "failed"
    elif result.passed and result.when == "call":
        item.status = "passed"

    pytest.test_failed = result.failed
    pytest.current_test_name = item.nodeid.split("::")[-1]


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_protocol(item: Item, nextitem: Optional[Item]) -> Generator[None, None, None]:
    """Track test metrics for each test using a context manager."""
    test_name = item.nodeid.split("::")[-1]
    metrics = ExecutionMetrics(test_name)
    with metrics:
        yield
        metrics.status = getattr(item, "status", "passed")
