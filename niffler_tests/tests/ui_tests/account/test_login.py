from internal.app import system_under_test as app
import pytest

from internal.data.models.user import User

pytestmark = [
    pytest.mark.allure_label("Account", label_type="epic"),
    pytest.mark.allure_label("Login", label_type="story"),
]


def test_a_registered_user_logging_in(in_browser, as_a_registered_user):
    user = as_a_registered_user

    app.auth_page.open()
    app.auth_page.log_in(user.username, user.password)

    app.auth_page.should_be_logged()


def test_a_random_user_logging_in(in_browser):
    user = User.random()

    app.auth_page.open()

    app.auth_page.fill_login(user.username)
    app.auth_page.fill_password(user.password)
    app.auth_page.submit()

    app.auth_page.should_display_invalid_credentials_message()


def test_logging_in_with_invalid_password(in_browser, as_a_registered_user):
    user = as_a_registered_user

    app.auth_page.open()

    app.auth_page.fill_login(user.username)
    app.auth_page.fill_password(user.username)
    app.auth_page.submit()

    app.auth_page.should_display_invalid_credentials_message()


def test_logging_out(in_browser, as_a_logged_user):
    _ = as_a_logged_user

    app.spendings_page.header.log_out()

    app.auth_page.should_be_not_logged()
