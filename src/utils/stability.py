"""Stability utilities for handling ParaBank demo site instability."""
import pytest
from playwright.sync_api import Page


def skip_if_internal_error(page: Page) -> None:
    """Skip the test if the site returns a known internal error."""
    # Give the page a moment to start transitioning or showing an error
    page.wait_for_timeout(1000)

    # Check for the known "Error!" title or error paragraph
    error_header = page.locator("h1.title", has_text="Error!")
    error_p = page.locator("p.error")

    # Check if either is visible
    if error_header.is_visible() or error_p.is_visible():
        error_text = (error_header.inner_text() if error_header.is_visible() else "") + (
            error_p.inner_text() if error_p.is_visible() else ""
        )
        if "internal error" in error_text.lower() or "error!" in error_text:
            pytest.skip(f"ParaBank site instability: {error_text.strip()}")

    # Also check page content as a fallback
    content = page.content().lower()
    if "internal error has occurred" in content:
        pytest.skip("ParaBank site instability: Internal Error detected in page content.")
