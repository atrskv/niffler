import os
import random
import time
from google.protobuf import internal
from grpc import insecure_channel, intercept_channel
import polling2
import pytest
import requests
from selene import browser, have

from internal import settings
from internal.clients.pb.niffler_currency_pb2_pbreflect import (
    NifflerCurrencyServiceClient,
)
from internal.clients.spends import SpendsHttpClient
from internal.interceptors.allure import AllureInterceptor
from internal.interceptors.logging import LoggingInterceptor
from internal.models.currency import Currency
from internal.models.user import User, fake
from internal.utils import random_recent_days

INTERCEPTORS = [LoggingInterceptor(), AllureInterceptor()]


@pytest.fixture(scope="session")
def gateway_url():
    return f"{settings.config.gateway_url}:{settings.config.gateway_port}"


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
        browser.driver.execute_script("localStorage.clear();")
        browser.driver.execute_script("sessionStorage.clear();")

    browser.quit()


@pytest.fixture(scope="function", autouse=False)
def as_a_random_user():
    user = User.create_random()

    yield user


@pytest.fixture(scope="function", autouse=False)
def as_a_registered_user(as_a_random_user):
    for attempt in range(5):
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

        time.sleep(5)

    raise Exception("Failed to register user after 5 attempts")


@pytest.fixture(scope="function", autouse=False)
def as_a_logged_user(as_a_registered_user):
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
            "username": user.login,
            "password": user.password,
        },
        headers={"X-XSRF-TOKEN": csrf_token},
        allow_redirects=True,
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


@pytest.fixture(scope="function")
def token(as_a_logged_user):
    for _ in range(10):
        token = browser.driver.execute_script(
            'return window.localStorage.getItem("access_token")'
        )
        if token:
            return token
        time.sleep(2)
    raise Exception("Access token not found in sessionStorage!")


@pytest.fixture(scope="function")
def spends_client(gateway_url, token) -> SpendsHttpClient:
    return SpendsHttpClient(gateway_url, token)


@pytest.fixture()
def spending_page(in_browser, as_a_logged_user):
    browser.open("/spending")
    browser.wait_until(have.url_containing("/spending"))
    user = as_a_logged_user
    yield user


@pytest.fixture
def category(request, spends_client):
    if hasattr(request, "param"):
        param = request.param
        names = [param] if isinstance(param, str) else list(param)
    else:
        names = [fake.word()]

    existing_categories = spends_client.get_categories()
    result = []

    for name in names:
        name = name.strip()

        existing = next(
            (
                c
                for c in existing_categories
                if c["name"].strip().lower() == name.lower()
            ),
            None,
        )

        if existing:
            result.append(existing)
            continue

        created = spends_client.add_category(name)

        result.append(created)
        existing_categories.append(created)

    polling2.poll(
        lambda: all(
            any(
                c["name"].strip().lower() == name.strip().lower()
                for c in spends_client.get_categories()
            )
            for name in names
        ),
        step=2,
        timeout=20,
    )

    return result[0] if len(result) == 1 else result


@pytest.fixture
def spends_with_single_category(request, spends_client, category):
    spends_params = getattr(
        request,
        "param",
        [
            {
                "amount": float(fake.random_int(min=10, max=100)),
                "currency": random.choice(list(Currency)).name.upper(),
                "description": fake.sentence(),
            },
            {
                "amount": float(fake.random_int(min=10, max=100)),
                "currency": random.choice(list(Currency)).name.upper(),
                "description": fake.sentence(),
            },
        ],
    )

    spends = []

    for p in spends_params:
        spend = spends_client.add_spend(
            category_id=category["id"],
            category_name=category["name"],
            username=category.get("username", "test_user"),
            currency=p["currency"],
            amount=p["amount"],
            description=p["description"],
            spend_date=random_recent_days(60),
            archived=category.get("archived", False),
        )

        spends.append(spend)

    return spends[0] if len(spends) == 1 else spends


@pytest.fixture
def spends_with_categories_1to1(request, spends_client, category):
    spends_params = getattr(
        request,
        "param",
        [
            {
                "amount": float(fake.random_int(min=10, max=100)),
                "currency": random.choice(list(Currency)).name.upper(),
                "description": fake.sentence(),
            },
            {
                "amount": float(fake.random_int(min=10, max=100)),
                "currency": random.choice(list(Currency)).name.upper(),
                "description": fake.sentence(),
            },
        ],
    )

    spends = []

    categories = category if isinstance(category, list) else [category]

    for c, p in zip(categories, spends_params):
        spend = spends_client.add_spend(
            category_id=c["id"],
            category_name=c["name"],
            username=c.get("username", "test_user"),
            currency=p["currency"],
            amount=p["amount"],
            description=p["description"],
            spend_date=random_recent_days(60),
            archived=c.get("archived", False),
        )

        spends.append(spend)

    return spends[0] if len(spends) == 1 else spends


@pytest.fixture(scope="session")
def grpc_client() -> NifflerCurrencyServiceClient:

    host = settings.config.currency_service_host

    if settings.config.use_mock:
        host = settings.config.wiremock_host

    channel = insecure_channel(host)
    intercepted_channel = intercept_channel(channel, *INTERCEPTORS)
    return NifflerCurrencyServiceClient(intercepted_channel)
