""" fixtures 
"""
import pytest
from playwright.sync_api import Page
from pages.home_login_page import HomePage
from pages.bill_pay_page import BillPay
from pages.helper_pom.payment_services_tab import PaymentServicesTab
from metrics_pusher import TestMetrics, push_metrics



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

# Initialize metrics when pytest session begins
def pytest_configure(config):
    # Push initial metrics to the Pushgateway
    push_metrics()
    print("Initial metrics pushed to Prometheus Pushgateway")
    
# Push final metrics when pytest session ends
def pytest_sessionfinish(session, exitstatus):
    push_metrics()
    print("Final metrics pushed to Prometheus Pushgateway")

# Track test metrics for each test
@pytest.hookimpl(tryfirst=True)
def pytest_runtest_protocol(item, nextitem):
    test_name = item.nodeid
    with TestMetrics(test_name):
        return None  # Let pytest handle the test execution

# Track test outcomes
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    
    # We only want to track the final test outcome
    if report.when == 'call':
        test_name = item.nodeid
        # TestMetrics will automatically track passes/failures