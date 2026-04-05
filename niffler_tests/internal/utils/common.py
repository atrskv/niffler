import random
import datetime
import requests
from selene import browser, have
import time
from internal import settings
from internal.data.models.user import User
import allure
import logging

def random_recent_days(days=30):
    now = datetime.datetime.now(datetime.timezone.utc)
    delta = datetime.timedelta(days=random.randint(0, days))
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


@allure.step
def wait_until_timeout(function):
    def wrapper(*args, **kwargs):
        default_timeout = 12
        timeout = kwargs.pop("timeout", default_timeout)
        polling_interval = kwargs.pop("polling_interval", 0.1)
        err = kwargs.pop("err", None)
        start_time = datetime.datetime.now().timestamp()
        result = None
        logging.debug(f'{start_time} start waiting')
        while datetime.datetime.now().timestamp() < start_time + timeout + 0.1:
            result = function(*args, **kwargs)
            if result is not None and result != [] and result != '':
                break
            time.sleep(polling_interval)
        if err and result is None:
            raise TimeoutError(
                f"{datetime.datetime.now().isoformat()} "
                f"Результаты функции {function.__name__} не найдены за {timeout}s"
            )
        if result is None:
            logging.error(f"{datetime.datetime.now().timestamp()} result is None")
        return result

    return wrapper