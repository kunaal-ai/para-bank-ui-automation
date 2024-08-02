""" fixtures 
"""
import pytest
from playwright.sync_api import Page
from pages.home_login_page import HomePage
from pages.bill_pay_page import BillPay
from pages.helper_pom.payment_services_tab import PaymentServicesTab



@pytest.fixture
def home_page(page: Page):
    return HomePage(page)

@pytest.fixture(scope="function")
def user_login(page: Page):
    hp = HomePage(page)
    hp.load()
    hp.user_log_in()
    yield

@pytest.fixture
def bill_pay_page(page: Page):
    return BillPay(page)

@pytest.fixture
def payment_services_tab(page: Page):
    return PaymentServicesTab(page)