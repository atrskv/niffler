import allure
import pytest
from allure_commons.reporter import AllureReporter
from allure_commons.types import AttachmentType
from allure_pytest.listener import AllureListener
from grpc import insecure_channel, intercept_channel
from pytest import FixtureDef, FixtureRequest, Item
from selene import browser

from internal import settings
from internal.clients.api.auth import AuthClient
from internal.clients.api.soap import SoapHttpClient
from internal.clients.api.spends import SpendsHttpClient
from internal.clients.api.users import UsersHttpClient
from internal.clients.db.spends import SpendDb
from internal.clients.pb.niffler_currency_pb2_pbreflect import (
    NifflerCurrencyServiceClient,
)
from internal.data.models.user import User
from internal.interceptors.allure import AllureInterceptor
from internal.interceptors.logging import LoggingInterceptor
from internal.settings import config
from internal.utils import log_in_user, register_user

INTERCEPTORS = [LoggingInterceptor(), AllureInterceptor()]


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


@pytest.fixture(scope="function")
def as_a_registered_user():
    user = User.random()
    register_user(user)
    return user


@pytest.fixture(scope="function")
def as_a_logged_user(as_a_registered_user, in_browser):
    user = as_a_registered_user
    log_in_user(user)
    return user


@pytest.fixture
def token(as_a_registered_user):
    user = as_a_registered_user
    token = AuthClient(config).auth(user.username, user.password)
    allure.attach(token, name="token.txt", attachment_type=AttachmentType.TEXT)
    return token


@pytest.fixture
def spends_client(token) -> SpendsHttpClient:
    return SpendsHttpClient(
        f"{settings.config.gateway_url}:{settings.config.gateway_port}", token
    )


@pytest.fixture(scope="session")
def spend_db() -> SpendDb:
    return SpendDb(settings.config.spend_db_url)


@pytest.fixture
def users_client(token) -> UsersHttpClient:
    return UsersHttpClient(
        f"{settings.config.gateway_url}:{settings.config.gateway_port}", token
    )


@pytest.fixture(scope="session")
def grpc_client() -> NifflerCurrencyServiceClient:
    host = settings.config.currency_service_host

    if settings.config.use_mock:
        host = settings.config.wiremock_host

    channel = insecure_channel(host)
    intercepted_channel = intercept_channel(channel, *INTERCEPTORS)

    return NifflerCurrencyServiceClient(intercepted_channel)


@pytest.fixture
def soap_session(token):

    service = SoapHttpClient(settings.config.soap_url, "")
    service.session.headers.update({"Content-Type": "text/xml; charset=utf-8"})

    return service
