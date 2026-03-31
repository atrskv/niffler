import random
from datetime import datetime, timezone, timedelta

import requests
from selene import browser, have

from internal import settings
from internal.data.models.user import User


def random_recent_days(days=30):
    now = datetime.now(timezone.utc)
    delta = timedelta(days=random.randint(0, days))
    return now - delta


def register_user(user: User):
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

    if response.status_code != 201:
        raise Exception("Failed to register user")


def log_in_user(user: User):
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
