import allure
import pytest
from allure_commons.reporter import AllureReporter
from allure_commons.types import AttachmentType
from allure_pytest.listener import AllureListener
from pytest import FixtureDef, FixtureRequest, Item
from selene import browser
from selenium.webdriver.chrome.options import Options
from internal import settings
from internal.clients.api.auth import AuthClient
from internal.interceptors.allure import AllureInterceptor
from internal.interceptors.logging import LoggingInterceptor
from internal.settings import config
from internal.utils.allure import add_screenshot, add_html, add_video

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


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        try:
            if hasattr(browser, 'driver') and browser.driver:
                add_screenshot()
                add_html()
        except Exception as e:
            print(f"Failed to capture failure artifacts: {e}")


@pytest.fixture(scope="function", autouse=False)
def in_browser():
    browser.config.base_url = settings.config.frontend_url
    browser.config.timeout = settings.config.timeout
    browser.config.window_width = settings.config.window_width
    browser.config.window_height = settings.config.window_height

    if settings.config.context == 'remote':
        selenoid_capabilities = {
            'browserName': settings.config.driver_name,
            'browserVersion': settings.config.driver_version,
            'selenoid:options': {
                'enableVNC': settings.config.enable_VNC,
                'enableVideo': settings.config.enable_video
            },
        }

        options = Options()
        options.capabilities.update(selenoid_capabilities)

        browser.config.driver_remote_url = f"{settings.config.selenoid_url}/wd/hub"
        browser.config.driver_options = options

        options.add_experimental_option(
            "prefs",
            {"intl.accept_languages": "ru,ru_RU"}
        )

    yield

    add_screenshot()
    add_html()

    if settings.config.context == 'remote':
        add_video()

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
