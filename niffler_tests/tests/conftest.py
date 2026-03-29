import random

import polling2
import requests
import pytest
from selene import browser, have
from grpc import insecure_channel, intercept_channel
import allure

from internal.settings import config
from internal import settings
from internal.clients.api.auth import AuthClient
from internal.clients.api.users import UsersHttpClient
from internal.clients.api.spends import SpendsHttpClient
from internal.clients.db.spends import SpendDb
from internal.clients.pb.niffler_currency_pb2_pbreflect import (
    NifflerCurrencyServiceClient,
)
from internal.interceptors.logging import LoggingInterceptor
from internal.interceptors.allure import AllureInterceptor
from internal.data.models.user import fake, User
from internal.data.models.spend import CategoryAPI, SpendAddAPI
from internal.data.models.currency import Currency
from internal.utils import random_recent_days
from allure_commons.types import AttachmentType
from allure_commons.reporter import AllureReporter
from allure_pytest.listener import AllureListener
from pytest import Item, FixtureDef, FixtureRequest

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


@pytest.fixture(scope="session")
def auth_api_token():
    token = AuthClient(config).auth(config.test_username, config.test_password)
    allure.attach(token, name="token.txt", attachment_type=AttachmentType.TEXT)
    return token


@pytest.fixture(scope="function", autouse=True)
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

    def _try_register():
        session = requests.Session()
        session.get(
            f"{settings.config.auth_url}:{settings.config.auth_port}/register",
            verify=False,
        )
        csrf_token = session.cookies.get("XSRF-TOKEN")

        response = session.post(
            f"{settings.config.auth_url}:{settings.config.auth_port}/register",
            data={
                "username": user.username,
                "password": user.password,
                "passwordSubmit": user.password,
                "_csrf": csrf_token,
            },
            headers={"X-XSRF-TOKEN": csrf_token},
            verify=False,
        )
        return response

    response = polling2.poll(
        target=_try_register,
        check_success=lambda r: r.status_code == 201,
        step=2.0,
        timeout=30.0,
    )

    if response.status_code != 201:
        raise Exception("Failed to register user")

    yield user


@pytest.fixture(scope="function")
def user(as_a_registered_user):
    return as_a_registered_user


@pytest.fixture(scope="function")
def as_a_logged_user(as_a_registered_user, in_browser):
    user = as_a_registered_user
    session = requests.Session()
    session.get(
        f"{settings.config.auth_url}:{settings.config.auth_port}/login", verify=False
    )
    csrf_token = session.cookies.get("XSRF-TOKEN")
    session.post(
        f"{settings.config.auth_url}:{settings.config.auth_port}/login",
        data={
            "_csrf": csrf_token,
            "username": user.username,
            "password": user.password,
        },
        headers={"X-XSRF-TOKEN": csrf_token},
        verify=False,
    )
    browser.open(settings.config.auth_url)
    for cookie in session.cookies:
        browser.driver.add_cookie(
            {
                "name": cookie.name,
                "value": cookie.value,
                "path": cookie.path or "/",
                "domain": cookie.domain or settings.config.auth_domain,
            }
        )
    browser.open(settings.config.frontend_url)
    browser.wait_until(have.url_containing("/main"))

    yield user


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


@pytest.fixture
def gateway_url():
    return f"{settings.config.gateway_url}:{settings.config.gateway_port}"


@pytest.fixture
def token(user):
    token = AuthClient(config).auth(user.username, user.password)
    allure.attach(token, name="token.txt", attachment_type=AttachmentType.TEXT)
    return token


@pytest.fixture
def spends_client(gateway_url, token) -> SpendsHttpClient:
    return SpendsHttpClient(gateway_url, token)


@pytest.fixture
def users_client(gateway_url, auth_api_token) -> UsersHttpClient:
    return UsersHttpClient(gateway_url, auth_api_token)


@pytest.fixture
def rollback_user(users_client, user):
    original = user.model_copy()
    yield
    users_client.update_user(original)


@pytest.fixture(scope="session")
def spend_db() -> SpendDb:
    return SpendDb(settings.config.spend_db_url)


@pytest.fixture(scope="session")
def grpc_client() -> NifflerCurrencyServiceClient:
    host = settings.config.currency_service_host
    if settings.config.use_mock:
        host = settings.config.wiremock_host
    channel = insecure_channel(host)
    intercepted_channel = intercept_channel(channel, *INTERCEPTORS)
    return NifflerCurrencyServiceClient(intercepted_channel)


@pytest.fixture
def category(
    request, spends_client: SpendsHttpClient, spend_db
) -> CategoryAPI | list[CategoryAPI]:
    if hasattr(request, "param"):
        param = request.param
        if isinstance(param, list):
            names = param
        elif isinstance(param, str):
            names = [param]
        else:
            names = [fake.word()]
    else:
        names = [fake.word()]

    existing_categories = spends_client.get_categories()

    result = []

    for name in names:
        existing = next(
            (c for c in existing_categories if c.name.lower() == name.lower()), None
        )
        if existing:
            result.append(existing)
        else:
            created = spends_client.add_category(name)
            result.append(created)
            existing_categories.append(created)

    yield result if len(result) > 1 else result[0]

    categories = result if isinstance(result, list) else [result]

    for c in categories:
        spend_db.delete_spends_by_category_id(c.id)
        spend_db.delete_category_by_id(c.id)


@pytest.fixture
def spends_with_single_category(request, spends_client, category: CategoryAPI, user):
    spends_params = getattr(
        request,
        "param",
        [
            SpendAddAPI(
                amount=float(fake.random_int(min=10, max=100)),
                currency=random.choice(list(Currency)).name.upper(),
                description=fake.sentence(),
                category=category.name,
            )
        ],
    )

    spends = []

    for spend in spends_params:
        if spend.category is None:
            spend.category = category.name
        spend.spendDate = random_recent_days(60).isoformat()
        created = spends_client.add_spend(spend, username=user.username)
        spends.append(created)

    return spends


@pytest.fixture
def spends_with_categories_1to1(request, spends_client, category, user):
    categories = category if isinstance(category, list) else [category]
    spends_params = getattr(request, "param", [])

    spends = []
    for c, spend in zip(categories, spends_params):
        spend.category = c.name
        spend.spendDate = random_recent_days(60).isoformat()
        created = spends_client.add_spend(spend, username=user.username)
        spends.append(created)

    return spends


@pytest.fixture
def rollback_spends(spends_client):
    created_spends = []
    yield created_spends
    if created_spends:
        spend_ids = [spend.id for spend in created_spends]
        spends_client.delete_spends(spend_ids)

