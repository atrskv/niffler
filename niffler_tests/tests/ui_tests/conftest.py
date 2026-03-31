import pytest
from selene import browser, have


@pytest.fixture
def spending_page(as_a_logged_user):
    browser.open("/spending")
    browser.wait_until(have.url_containing("/spending"))
    yield as_a_logged_user


@pytest.fixture
def home_page(as_a_logged_user):
    browser.open("/main")
    browser.wait_until(have.url_containing("/main"))
    yield as_a_logged_user
