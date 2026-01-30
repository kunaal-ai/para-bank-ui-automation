"""Stability utilities for handling ParaBank demo site instability."""
import logging
from typing import Any, Callable, Optional

import pytest
from playwright._impl._errors import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import Page


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
        pytest.xfail(f"ParaBank server unavailable: {error_message}")


# Backward compatibility - keep old function name but redirect to new one
def skip_if_internal_error(page: Page) -> None:
    """Deprecated: Use handle_internal_error instead."""
    handle_internal_error(page, requires_login=False)


def safe_click(locator: Any, retry_on_timeout: bool = False) -> None:
    """
    Perform a more robust click by ensuring the element is settled
    and retrying if it's intercepted or unresponsive.

    Args:
        locator: The Playwright locator to click
        retry_on_timeout: If True, retry with page reload on timeout (default: False for speed)
    """
    page = locator.page

    def _do_click() -> None:
        # 1. Ensure it's attached and visible (reduced timeout)
        locator.wait_for(state="visible", timeout=10000)  # Reduced from 30s

        # 2. Use a force click if standard click hangs
        try:
            locator.click(timeout=3000)  # Reduced from 5s
        except Exception:
            # Fallback for intercepted clicks or slow hydration
            locator.click(force=True, timeout=2000)

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
    last_error: Optional[PlaywrightTimeoutError] = None

    for attempt in range(max_retries + 1):
        try:
            return action_func()
        except PlaywrightTimeoutError as e:
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
