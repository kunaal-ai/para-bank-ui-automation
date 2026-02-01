"""Stability utilities for handling ParaBank demo site instability."""
import logging
import time
from typing import Any, Callable, Optional

from playwright._impl._errors import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import Locator, Page


def handle_internal_error(page: Page, requires_login: bool = True) -> None:
    """Handle ParaBank internal errors appropriately based on test requirements.

    For login-required tests: Mark as xfail (conditional pass) when server error occurs.
    For non-login tests: Don't interfere, let the test continue and report actual results.

    Args:
        page: The Playwright page object
        requires_login: Whether this test requires authentication (default: True)
    """
    # Check for the known "Error!" title or error paragraph
    # Use a short timeout to not slow down healthy runs
    error_detected = False
    error_message = ""

    try:
        error_header = page.locator("h1.title", has_text="Error!")
        error_p = page.locator("p.error")

        if error_header.is_visible(timeout=500) or error_p.is_visible(timeout=500):
            error_text = (error_header.inner_text() if error_header.is_visible() else "") + (
                error_p.inner_text() if error_p.is_visible() else ""
            )
            if "internal error" in error_text.lower() or "error!" in error_text:
                error_detected = True
                error_message = error_text.strip()
    except Exception:  # nosec B110
        pass  # Intentionally ignore errors during error detection

    # Also check page content as a fallback for the specific error message
    if not error_detected:
        content = page.content().lower()
        if "internal error has occurred" in content or "internal error has occured" in content:
            error_detected = True
            error_message = "Internal Error detected - server is experiencing issues"

    # Only handle the error if it was detected and test requires login
    if error_detected and requires_login:
        logger = logging.getLogger("parabank")
        logger.warning(f"Internal Error intercepted: {error_message}")
        raise ParaBankInternalError(f"ParaBank server unavailable: {error_message}")


class ParaBankInternalError(Exception):
    """Raised when ParaBank returns a known internal error page."""


# Backward compatibility - keep old function name but redirect to new one
def skip_if_internal_error(page: Page) -> None:
    """Deprecated: Use handle_internal_error instead."""
    handle_internal_error(page, requires_login=False)


def safe_click(locator: Any, retry_on_timeout: bool = False, timeout: int = 10000) -> None:
    """
    Perform a more robust click by ensuring the element is settled
    and retrying if it's intercepted or unresponsive.

    Args:
        locator: The Playwright locator to click
        retry_on_timeout: If True, retry with page reload on timeout (default: False for speed)
        timeout: Timeout for the click operation in milliseconds (default: 10000)
    """
    # Handle the fact that locator might be a locator or just a thing that has a page
    page = locator.page

    def _do_click() -> None:
        # 1. Ensure it's attached and visible (balanced timeout for slow server)
        locator.wait_for(state="visible", timeout=20000)

        # We avoid blind fallbacks for clicks that might trigger server-side state changes
        # (like registration)
        locator.click(timeout=timeout)

    if retry_on_timeout:
        retry_with_reload(page, _do_click, max_retries=1)
    else:
        _do_click()


def retry_with_reload(
    page: Page, action_func: Callable[[], Any], max_retries: int = 1
) -> Optional[Any]:
    """Retry an action with page reload if it times out.

    This handles cases where ParaBank server is slow/unresponsive and causes
    timeout errors. Instead of failing immediately, we reload the page and retry.

    Args:
        page: The Playwright page object
        action_func: A callable that performs the action (e.g., lambda: locator.click())
        max_retries: Maximum number of retries (default: 1)

    Returns:
        The result of action_func if successful

    Raises:
        The original exception if all retries fail
    """
    logger = logging.getLogger("parabank")
    last_error: Optional[Exception] = None

    for attempt in range(max_retries + 1):
        try:
            return action_func()
        except (PlaywrightTimeoutError, Exception) as e:
            if not isinstance(e, PlaywrightTimeoutError) and "timeout" not in str(e).lower():
                raise e

            last_error = e
            if attempt < max_retries:
                logger.warning(f"Timeout on attempt {attempt + 1}, reloading page and retrying...")
                page.reload(
                    timeout=30000, wait_until="domcontentloaded"
                )  # Reduced from networkidle
                page.wait_for_timeout(500)  # Reduced from 2000ms
            else:
                logger.error(f"All {max_retries + 1} attempts failed")
                raise

    # Should never reach here, but just in case
    if last_error:
        raise last_error
    return None


def wait_for_options(locator: Locator, min_options: int = 1, timeout: int = 15000) -> None:
    """Wait for a select/dropdown to have at least min_options.

    This uses a polling loop for maximum reliability in parallel execution.
    """
    logger = logging.getLogger("parabank")
    start_time = time.time()

    while time.time() - start_time < (timeout / 1000):
        try:
            options = locator.locator("option").all_inner_texts()
            # Filter out empty options or "Loading..."
            valid_options = [o for o in options if o.strip() != "" and "loading" not in o.lower()]
            if len(valid_options) >= min_options:
                return
        except Exception:
            pass  # nosec: B110 (Expected timeout/visibility failure)

        time.sleep(0.5)

    logger.warning(f"Timed out waiting for {min_options} options in dropdown after {timeout}ms")
    # Raise a clear error if it fails
    raise PlaywrightTimeoutError(
        f"Dropdown did not populate with {min_options} options in {timeout}ms"
    )
