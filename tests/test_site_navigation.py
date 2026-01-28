"""Tests for general site navigation and footer links."""
import pytest
from playwright.sync_api import Page, expect

from tests.pages.home_login_page import HomePage

pytestmark = pytest.mark.usefixtures("user_login")


def test_footer_about_us_navigation(page: Page, base_url: str) -> None:
    """Verify navigation to About Us via footer link."""
    home_page = HomePage(page)
    home_page.load(base_url)
    page.locator("#footerPanel").get_by_role("link", name="About Us").click()
    expect(page.locator("h1.title")).to_have_text("ParaSoft Demo Website", timeout=10000)


def test_footer_services_navigation(page: Page, base_url: str) -> None:
    """Verify navigation to Services via footer link."""
    home_page = HomePage(page)
    home_page.load(base_url)
    page.locator("#footerPanel").get_by_role("link", name="Services").last.click()
    expect(page.locator("span.heading").first).to_contain_text("services", timeout=10000)


def test_home_page_logo_navigation(page: Page, base_url: str) -> None:
    """Verify that clicking the logo returns to the home page."""
    home_page = HomePage(page)
    home_page.load(base_url)
    # Go to about us first
    page.locator("ul.leftmenu").get_by_role("link", name="About Us").click()
    # Click logo
    page.locator("img[title='ParaBank']").click()
    expect(page).to_have_url(f"{base_url.rstrip('/')}/index.htm", timeout=10000)


def test_header_home_link(page: Page, base_url: str) -> None:
    """Verify the 'home' icon link in the header."""
    home_page = HomePage(page)
    home_page.load(base_url)
    page.locator("ul.button").get_by_role("link", name="home").click()
    expect(page).to_have_url(f"{base_url.rstrip('/')}/index.htm", timeout=10000)


def test_header_contact_link(page: Page, base_url: str) -> None:
    """Verify the 'contact' icon link in the header."""
    home_page = HomePage(page)
    home_page.load(base_url)
    page.locator("ul.button").get_by_role("link", name="contact").click()
    expect(page.locator("h1.title")).to_have_text("Customer Care", timeout=10000)


def test_header_about_link(page: Page, base_url: str) -> None:
    """Verify the 'about' icon link in the header."""
    home_page = HomePage(page)
    home_page.load(base_url)
    page.locator("ul.button").get_by_role("link", name="about").click()
    expect(page.locator("h1.title")).to_have_text("ParaSoft Demo Website", timeout=10000)
