import os
import time

import pytest
import requests
from dotenv import load_dotenv
from selene import browser

from niffler_tests.internal.models.user import User


@pytest.fixture(scope="session", autouse=True)
def load_env():
    _ = load_dotenv()


@pytest.fixture(scope="function", autouse=False)
def in_browser():
    browser.config.base_url = f"{os.getenv('FRONTEND_URL')}"
    browser.config.timeout = 6.0


@pytest.fixture(scope="function", autouse=False)
def registered_user():
    for attempt in range(5):
        session = requests.Session()
        session.get(
            f"{os.getenv('AUTH_URL')}:{os.getenv('AUTH_PORT')}/register",
            verify=False,
        )

        csrf_token = session.cookies.get("XSRF-TOKEN")

        user = User.create_random()
        response = session.post(
            f"{os.getenv('AUTH_URL')}:{os.getenv('AUTH_PORT')}/register",
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
def as_logged_user(registered_user):
    user = registered_user

    session = requests.Session()
    session.get(
        f"{os.getenv('AUTH_URL')}:{os.getenv('AUTH_PORT')}/login", verify=False
    )
    csrf_token = session.cookies.get("XSRF-TOKEN")

    session.post(
        f"{os.getenv('AUTH_URL')}:{os.getenv('AUTH_PORT')}/login",
        data={
            "_csrf": csrf_token,
            "username": user.login,
            "password": user.password,
        },
        headers={"X-XSRF-TOKEN": csrf_token},
        allow_redirects=True,
        verify=False,
    )

    browser.open(f"{os.getenv('AUTH_URL')}")

    for cookie in session.cookies:
        browser.driver.add_cookie(
            {
                "name": cookie.name,
                "value": cookie.value,
                "path": cookie.path or "/",
                "domain": cookie.domain or f"{os.getenv('AUTH_DOMAIN')}",
            }
        )

    browser.open(f"{os.getenv('FRONTEND_URL')}")

    yield user


@pytest.fixture(autouse=True)
def clean_all_state():
    yield

    for url in [
        os.getenv("FRONTEND_URL"),
        f"{os.getenv('AUTH_URL')}:{os.getenv('AUTH_PORT')}",
    ]:
        browser.open(url)
        browser.driver.delete_all_cookies()
        browser.driver.execute_script("localStorage.clear();")
        browser.driver.execute_script("sessionStorage.clear();")
