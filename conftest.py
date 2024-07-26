""" fixtures 
"""
import pytest
from playwright.sync_api import Page
from pages.home_login_page import HomePage


@pytest.fixture
def home_page(page: Page):
    return HomePage(page)

@pytest.fixture(scope="function")
def user_login(page: Page):
    hp = HomePage(page)
    hp.load()
    hp.user_log_in()
    yield