from internal.app import system_under_test as app
import pytest

from internal.data.models.user import User


def test_a_registered_user_logging_in(as_a_registered_user, in_browser):
    user = as_a_registered_user
    _ = in_browser

    app.auth_page.open()
    app.auth_page.log_in(user.username, user.password)

    app.auth_page.should_be_logged()


def test_a_random_user_logging_in(in_browser):
    user = User.random()
    _ = in_browser

    app.auth_page.open()
    app.auth_page.fill_login(user.username)
    app.auth_page.fill_password(user.password)
    app.auth_page.submit()

    app.auth_page.should_display_invalid_credentials_message()


def test_logging_in_with_invalid_password(as_a_registered_user, in_browser):
    user = as_a_registered_user
    _ = in_browser

    app.auth_page.open()
    app.auth_page.fill_login(user.username)
    app.auth_page.fill_password(user.username)
    app.auth_page.submit()

    app.auth_page.should_display_invalid_credentials_message()


def test_logging_out(as_a_logged_user, in_browser):
    _ = as_a_logged_user, in_browser

    app.spendings_page.header.log_out()

    app.auth_page.should_be_not_logged()


pytestmark = [
    pytest.mark.allure_label("UI: Account and spends", label_type="epic"),
    pytest.mark.allure_label("Account", label_type="feature"),
    pytest.mark.allure_label("Login", label_type="story"),
]
