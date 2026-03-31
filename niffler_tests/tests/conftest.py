import allure
import pytest
from allure_commons.reporter import AllureReporter
from allure_commons.types import AttachmentType
from allure_pytest.listener import AllureListener
from pytest import FixtureDef, FixtureRequest, Item
from selene import browser

from internal import settings
from internal.clients.api.auth import AuthClient
from internal.interceptors.allure import AllureInterceptor
from internal.interceptors.logging import LoggingInterceptor
from internal.settings import config

INTERCEPTORS = [LoggingInterceptor(), AllureInterceptor()]

pytest_plugins = [
    "internal.fixtures.pages",
    "internal.fixtures.spends",
    "internal.fixtures.rollbacks",
    "internal.fixtures.users",
    "internal.fixtures.clients",
]


def allure_logger(config) -> AllureReporter:
    listener: AllureListener = config.pluginmanager.get_plugin("allure_listener")
    return listener.allure_logger


@pytest.hookimpl(hookwrapper=True, trylast=True)
def pytest_runtest_call(item: Item):

    yield

    allure.dynamic.title(" ".join(item.name.split("_")[1:]).title())


@pytest.hookimpl(hookwrapper=True, trylast=True)
def pytest_fixture_setup(fixturedef: FixtureDef, request: FixtureRequest):

    yield

    logger = allure_logger(request.config)
    item = logger.get_last_item()
    scope_letter = fixturedef.scope[0].upper()
    item.name = f"[{scope_letter}] " + " ".join(fixturedef.argname.split("_")).title()


@pytest.fixture(scope="function", autouse=False)
def in_browser():
    browser.config.base_url = settings.config.frontend_url
    browser.config.timeout = settings.config.timeout

    yield

    for url in [
        settings.config.frontend_url,
        f"{settings.config.auth_url}:{settings.config.auth_port}",
    ]:
        browser.open(url)
        browser.driver.delete_all_cookies()
        browser.driver.execute_script("localStorage.clear(); sessionStorage.clear();")

    browser.quit()


@pytest.fixture
def token(as_a_registered_user):
    user = as_a_registered_user
    token = AuthClient(config).auth(user.username, user.password)
    allure.attach(token, name="token.txt", attachment_type=AttachmentType.TEXT)
    return token
