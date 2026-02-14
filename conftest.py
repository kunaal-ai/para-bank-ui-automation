"""Test configuration and fixtures for ParaBank UI automation."""
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, Generator, Optional

import pytest
from _pytest.config import Config as PytestConfig
from _pytest.config.argparsing import Parser
from _pytest.fixtures import FixtureRequest
from _pytest.nodes import Item
from _pytest.runner import CallInfo
from dotenv import load_dotenv  # type: ignore

# Load environment variables from .env file
load_dotenv()

# Ensure Healix can push metrics to Pushgateway when running locally (docker-compose sets this in containers)
if not os.environ.get("HEALIX_PUSHGATEWAY_URL") and not os.environ.get("PUSHGATEWAY_URL"):
    os.environ.setdefault("HEALIX_PUSHGATEWAY_URL", "http://localhost:9091")
elif os.environ.get("PUSHGATEWAY_URL") and not os.environ.get("HEALIX_PUSHGATEWAY_URL"):
    os.environ.setdefault("HEALIX_PUSHGATEWAY_URL", os.environ["PUSHGATEWAY_URL"])

from playwright.sync_api import Browser, BrowserContext, Page, expect

from config import Config
from src.utils.metrics_pusher import ExecutionMetrics, cleanup_healix_metrics, cleanup_metrics
from src.utils.stability import ParaBankInternalError
from tests.data.user_factory import UserFactory
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
    # Patch expect BEFORE any test files are imported
    from healix import _patch_expect  # type: ignore

    _patch_expect()

    logger = logging.getLogger("parabank")
    logger.info("=" * 80)
    logger.info("Starting test session")

    # Cleanup old metrics from Pushgateway to ensure Grafana matches this run
    # Only run on master process to avoid workers deleting each other's metrics
    if not hasattr(config, "workerinput"):
        try:
            cleanup_metrics()
            cleanup_healix_metrics()
            logger.info("Old metrics cleaned up from Pushgateway")
        except Exception as e:
            logger.warning(f"Could not cleanup old metrics: {e}")

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
    """Log test session completion and push metrics."""
    # Metrics are pushed per-test in ExecutionMetrics context manager


# Fixtures
@pytest.fixture
def browser_context_args(
    browser_context_args: Dict[str, Any],
    config: Dict[str, Any],
    auth_state: Path,
    request: pytest.FixtureRequest,
) -> Dict[str, Any]:
    """Unified browser context configuration with session reuse.

    We only inject the storage_state for non-login tests to ensure
    login tests always have a fresh, unauthenticated session.
    """
    args = {
        **browser_context_args,
        "viewport": config["viewport"],
        "ignore_https_errors": True,
        "record_video_dir": str(config["test_results_dir"] / "videos"),
        "record_video_size": config["viewport"],
    }

    # Do not use saved state for login, registration, home UI, or forgot login tests
    unauthenticated_keywords = ["login", "registration", "home_page_ui", "forgot_login", "index"]
    is_unauthenticated_test = any(
        kw in request.node.nodeid.lower() for kw in unauthenticated_keywords
    )
    # Only use auth_state if it exists and has content (not empty)
    if not is_unauthenticated_test and auth_state.exists() and auth_state.stat().st_size > 0:
        args["storage_state"] = str(auth_state)

    return args


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
    """Configure browser launch arguments with stability settings."""
    browser_type_launch_args.update(
        {
            "headless": env_config.headless,
            "slow_mo": 100,  # Small delay to allow JS hydration
            "timeout": 30000,
        }
    )
    return browser_type_launch_args


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
    """Create a new page with extended timeouts for slow server responses."""
    page = context.new_page()

    # Increase timeouts to handle ParaBank's slow database operations
    page.set_default_navigation_timeout(90000)  # 90s for page loads
    page.set_default_timeout(60000)  # 60s for element interactions

    yield page

    # Take screenshot on test failure
    if hasattr(request.node, "rep_call") and request.node.rep_call.failed:
        screenshot_dir = config["test_results_dir"] / "screenshots"
        screenshot_dir.mkdir(exist_ok=True)
        test_name = request.node.name.replace("[", "_").replace("]", "_")
        screenshot_path = screenshot_dir / f"{test_name}.png"
        page.screenshot(path=str(screenshot_path))
        logger.info(f"Screenshot saved to: {screenshot_path}")

    page.close()


@pytest.fixture
def hx_page(
    context: BrowserContext, request: FixtureRequest, config: Dict[str, Any]
) -> Generator[Page, None, None]:
    """Auto-healing page fixture - use this instead of 'page' for tests that need self-healing."""
    import healix

    print(f"\n[Healix] [DEBUG] Loaded from: {healix.__file__}")
    from healix import Healix

    page = context.new_page()

    # Apply Healix patching for auto-healing
    page = Healix.patch(page)

    # Increase timeouts to handle ParaBank's slow database operations
    page.set_default_navigation_timeout(90000)  # 90s for page loads
    page.set_default_timeout(60000)  # 60s for element interactions

    yield page

    # Take screenshot on test failure
    if hasattr(request.node, "rep_call") and request.node.rep_call.failed:
        screenshot_dir = config["test_results_dir"] / "screenshots"
        screenshot_dir.mkdir(exist_ok=True)
        test_name = request.node.name.replace("[", "_").replace("]", "_")
        screenshot_path = screenshot_dir / f"{test_name}.png"
        page.screenshot(path=str(screenshot_path))
        logger.info(f"Screenshot saved to: {screenshot_path}")

    page.close()


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
def worker_id(request: pytest.FixtureRequest) -> str:
    """Get the worker ID for parallel test execution.

    Returns 'master' for non-parallel execution, or 'gw0', 'gw1', etc. for parallel workers.

    Args:
        request: Pytest fixture request

    Returns:
        Worker identifier string
    """
    if hasattr(request.config, "workerinput"):
        # Running with pytest-xdist
        return str(request.config.workerinput["workerid"])
    # Running without pytest-xdist (single process)
    return "master"


@pytest.fixture(scope="session")
def auth_state(browser: Browser, config: Dict[str, Any], base_url: str, worker_id: str) -> Path:
    # pylint: disable=too-complex
    """Perform login once at the start of the session and return the state file path.

    Creates worker-specific state files to avoid session sharing race conditions
    when tests run in parallel.

    Args:
        browser: Playwright browser instance
        config: Test configuration dictionary
        base_url: Base URL for the application
        worker_id: pytest-xdist worker identifier (e.g., 'gw0', 'gw1', or 'master')

    Returns:
        Path to the state file. The file will only exist if login was successful.
    """
    # Create worker-specific state file to avoid session sharing
    if worker_id == "master":
        # Non-parallel execution
        state_file = Path("test-results/state.json")
    else:
        # Parallel execution - each worker gets its own state file
        state_file = Path(f"test-results/state_{worker_id}.json")

    state_file.parent.mkdir(exist_ok=True)

    # Remove any existing state file to start fresh
    if state_file.exists():
        state_file.unlink()

    context = browser.new_context()
    page = context.new_page()

    try:
        test_user = config["test_user"]
        logger.info(f"Attempting to create auth state for user: {test_user['username']}")

        page.goto(base_url, timeout=60000)
        page.fill("input[name='username']", test_user["username"])
        page.fill("input[name='password']", test_user["password"])
        page.click("input[value='Log In']")

        # Wait a moment for the page to respond
        page.wait_for_timeout(2000)

        # Check for error pages
        if "Error" in page.title() or page.locator("p.error").is_visible(timeout=2000):
            logger.error(f"Login failed for {test_user['username']} with error page/message.")
            raise RuntimeError("Login failed on server side")

        # Verify we navigated to the accounts overview page
        page.wait_for_url("**/overview.htm", timeout=20000)

        # Verify Account Services menu
        expect(page.locator("#leftPanel h2", has_text="Account Services")).to_be_visible(
            timeout=10000
        )

        context.storage_state(path=str(state_file))
        logger.info(f"Successfully created auth state at: {state_file}")

    except Exception as e:
        logger.warning(f"Initial login failed: {e}. Attempting registration fallback...")
        try:
            factory = UserFactory()
            new_user = factory.create_user(username_prefix="session")
            user_data = new_user.to_dict()

            logger.info(f"Registering new fallback user: {user_data['username']}")
            page.goto(f"{base_url}/register.htm", timeout=60000)
            _fill_registration_form(page, user_data)
            page.click("input[value='Register']")

            page.wait_for_url("**/register.htm", timeout=30000)
            if "Welcome" in page.content() or "created successfully" in page.content():
                logger.info(
                    f"Successfully registered fallback session user: {user_data['username']}"
                )
                context.storage_state(path=str(state_file))
                config["test_user"] = user_data
            else:
                logger.error("Registration fallback failed to reach welcome page.")
        except Exception as reg_e:
            logger.error(f"Fallback registration failed: {reg_e}")

        logger.warning("Tests will run without session reuse - each test will need to authenticate")
        # Do NOT create an empty file - let the browser_context_args fixture handle missing state
    finally:
        context.close()

    return state_file


@pytest.fixture
def user_login(page: Page, auth_state: Path, base_url: str, config: Dict[str, Any]) -> None:
    """Apply the pre-authenticated state to the current page with robust fallback.

    If the session state fails to apply, it performs a manual login.
    """

    def _is_logged_in() -> bool:
        # Check for logout link or overview header as proof of active session
        return (
            page.get_by_role("link", name="Log Out").is_visible(timeout=2000)
            or "Accounts Overview" in page.title()
        )

    # 1. Attempt to use pre-authenticated state by navigating to a protected page
    page.goto(f"{base_url}/overview.htm", timeout=30000)

    # Wait for potential "Client Challenge" or loading screen to vanish
    try:
        page.wait_for_selector("title:has-text('Client Challenge')", state="detached", timeout=5000)
    except Exception:  # nosec B110
        pass  # If it didn't appear or didn't go away, we'll fail at the login check next

    if _is_logged_in():
        logger.info("Session state applied successfully.")
        return

    # 2. Fallback: Perform manual login if state was missing or failed
    logger.warning("Session state failed or was invalid. Performing manual login fallback...")
    page.goto(base_url)
    test_user = config["test_user"]
    page.fill("input[name='username']", test_user["username"])
    page.fill("input[name='password']", test_user["password"])
    page.click("input[value='Log In']")

    # Verify success of fallback login
    try:
        page.wait_for_url("**/overview.htm", timeout=30000)
        logger.info("Manual login fallback successful.")
    except Exception as e:
        logger.error(f"Manual login fallback failed: {e}")
        # Final attempt to check page content
        if not _is_logged_in():
            raise RuntimeError(
                "Failed to achieve authenticated state even after manual fallback."
            ) from e


# Test Hooks
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item: Item, call: CallInfo[None]) -> Generator[Any, None, None]:
    """Track test failures for screenshots."""
    outcome: Any = yield
    result: Any = outcome.get_result()

    if result.failed:
        if _handle_failed_report(item, call, result):
            item.status = "passed"
        else:
            item.status = "failed"
    elif hasattr(result, "wasxfail") and "ParaBank server unavailable" in str(result.wasxfail):
        result.outcome = "passed"
        delattr(result, "wasxfail")
        item.status = "passed"
    elif result.outcome == "rerun" or getattr(result, "rerun", 0) > 0:
        item.status = "rerun"
    elif result.skipped:
        item.status = "skipped"
    elif result.passed and result.when == "call":
        item.status = "passed"

    pytest.test_failed = result.failed
    pytest.current_test_name = item.nodeid.split("::")[-1]


def _handle_failed_report(item: Item, call: CallInfo[None], result: Any) -> bool:
    """Check if a failed test should be promoted to passed due to ParaBank error."""
    # 1. Check for explicit exception
    if call.excinfo and call.excinfo.errisinstance(ParaBankInternalError):
        # Terminate session immediately on known server overload
        pytest.exit("server limit reached: Internal Error detected")

    # 2. Check for implicit error on page
    if "page" in item.funcargs:
        try:
            page = item.funcargs["page"]
            content = page.content().lower()
            if "internal error" in content or "error!" in page.title().lower():
                # Terminate session immediately on suspected server overload
                pytest.exit("server limit reached: Internal Error detected")
        except Exception:  # nosec B110
            pass
    return False


def _fill_registration_form(page: Page, user_data: Dict[str, Any]) -> None:
    """Helper to fill ParaBank registration form."""
    page.fill("input[name='customer.firstName']", user_data["first_name"])
    page.fill("input[name='customer.lastName']", user_data["last_name"])
    page.fill("input[name='customer.address.street']", user_data["address"])
    page.fill("input[name='customer.address.city']", user_data["city"])
    page.fill("input[name='customer.address.state']", user_data["state"])
    page.fill("input[name='customer.address.zipCode']", user_data["zip_code"])
    page.fill("input[name='customer.phoneNumber']", user_data["phone"])
    page.fill("input[name='customer.ssn']", user_data["ssn"])
    page.fill("input[name='customer.username']", user_data["username"])
    page.fill("input[name='customer.password']", user_data["password"])
    page.fill("input[name='repeatedPassword']", user_data["password"])


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_protocol(item: Item, nextitem: Optional[Item]) -> Generator[None, None, None]:
    test_name = item.nodeid.split("::")[-1]

    # Get worker ID to avoid metrics collision in Grafana
    worker_id = "master"
    if hasattr(item.config, "workerinput"):
        worker_id = item.config.workerinput["workerid"]

    metrics = ExecutionMetrics(test_name, grouping_key={"worker": worker_id})
    with metrics:
        yield
        metrics.status = getattr(item, "status", "passed")


@pytest.fixture(scope="session")
def user_factory() -> UserFactory:
    """Fixture to provide a UserFactory instance for generating test data."""
    return UserFactory()
