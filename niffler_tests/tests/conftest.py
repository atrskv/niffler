import random
import time

import pytest
import requests
from grpc import insecure_channel, intercept_channel
from selene import browser, have
from internal.clients.db.spends import SpendDb
from internal import settings
from internal.clients.pb.niffler_currency_pb2_pbreflect import (
    NifflerCurrencyServiceClient,
)
from internal.clients.spends import SpendsHttpClient
from internal.interceptors.allure import AllureInterceptor
from internal.interceptors.logging import LoggingInterceptor
from internal.data.models.currency import Currency
from internal.data.models.user import User, fake
from internal.data.models.spend import CategoryAPI, SpendAddAPI
from internal.utils import random_recent_days

INTERCEPTORS = [LoggingInterceptor(), AllureInterceptor()]


@pytest.fixture(scope="session")
def gateway_url():
    return f"{settings.config.gateway_url}:{settings.config.gateway_port}"


@pytest.fixture(scope="function")
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
        browser.driver.execute_script("localStorage.clear();")
        browser.driver.execute_script("sessionStorage.clear();")

    browser.quit()


@pytest.fixture
def as_a_random_user():
    user = User.create_random()
    yield user


@pytest.fixture
def as_a_registered_user(as_a_random_user):
    for _ in range(5):
        session = requests.Session()
        session.get(
            f"{settings.config.auth_url}:{settings.config.auth_port}/register",
            verify=False,
        )

        csrf_token = session.cookies.get("XSRF-TOKEN")
        user = as_a_random_user

        response = session.post(
            f"{settings.config.auth_url}:{settings.config.auth_port}/register",
            data={
                "username": user.login,
                "password": user.password,
                "passwordSubmit": user.password,
                "_csrf": csrf_token,
            },
            headers={"X-XSRF-TOKEN": csrf_token},
            verify=False,
        )

        if response.status_code == 201:
            yield user
            return

        time.sleep(2)

    raise Exception("Failed to register user")


@pytest.fixture
def as_a_logged_user(as_a_registered_user):
    user = as_a_registered_user

    session = requests.Session()
    session.get(
        f"{settings.config.auth_url}:{settings.config.auth_port}/login",
        verify=False,
    )

    csrf_token = session.cookies.get("XSRF-TOKEN")

    session.post(
        f"{settings.config.auth_url}:{settings.config.auth_port}/login",
        data={
            "_csrf": csrf_token,
            "username": user.login,
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
def token(as_a_logged_user):
    for _ in range(10):
        token = browser.driver.execute_script(
            'return window.localStorage.getItem("access_token")'
        )
        if token:
            return token
        time.sleep(1)

    raise Exception("Access token not found")


@pytest.fixture()
def spending_page(in_browser, as_a_logged_user):
    browser.open("/spending")
    browser.wait_until(have.url_containing("/spending"))
    user = as_a_logged_user
    yield user


@pytest.fixture
def spends_client(gateway_url, token) -> SpendsHttpClient:
    return SpendsHttpClient(gateway_url, token)


@pytest.fixture(scope="session")
def spend_db() -> SpendDb:
    return SpendDb(settings.config.spend_db_url)


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
def spends_with_single_category(request, spends_client, category: CategoryAPI):
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
        created = spends_client.add_spend(spend, username=category.username)
        spends.append(created)

    return spends


@pytest.fixture
def spends_with_categories_1to1(request, spends_client, category):
    categories = category if isinstance(category, list) else [category]
    spends_params = getattr(request, "param", [])

    spends = []
    for c, spend in zip(categories, spends_params):
        spend.category = c.name
        spend.spendDate = random_recent_days(60).isoformat()
        created = spends_client.add_spend(spend, username=c.username)
        spends.append(created)

    return spends


@pytest.fixture(scope="session")
def grpc_client() -> NifflerCurrencyServiceClient:
    host = settings.config.currency_service_host

    if settings.config.use_mock:
        host = settings.config.wiremock_host

    channel = insecure_channel(host)
    intercepted_channel = intercept_channel(channel, *INTERCEPTORS)

    return NifflerCurrencyServiceClient(intercepted_channel)
