from internal.app import system_under_test as app
from internal.data.models.user import fake, User
import pytest


pytestmark = [
    pytest.mark.allure_label("UI: Account and spends", label_type="epic"),
    pytest.mark.allure_label("Account", label_type="feature"),
    pytest.mark.allure_label("Registration", label_type="story"),
]


def test_registering_a_user(in_browser):
    user = User.random()

    app.auth_page.open()
    app.auth_page.go_to_register()
    app.register_page.register(user.username, user.password)

    app.register_page.should_be_registered()


def test_registering_with_a_short_username(in_browser):
    user = User.random()

    app.auth_page.open()
    app.auth_page.go_to_register()
    app.register_page.fill_login(user.username[:2])
    app.register_page.fill_password(user.password)
    app.register_page.fill_submut_password(user.password)
    app.register_page.submut()

    app.register_page.should_login_length_error_be_visible()


def test_registering_with_a_long_username(in_browser):
    user = User.random()
    user.username = fake.pystr(min_chars=51, max_chars=51)

    app.auth_page.open()
    app.auth_page.go_to_register()
    app.register_page.fill_login(user.username)
    app.register_page.fill_password(user.password)
    app.register_page.fill_submut_password(user.password)
    app.register_page.submut()

    app.register_page.should_login_length_error_be_visible()


def test_registering_with_a_short_password(in_browser):
    user = User.random()
    user.password = user.password[:2]

    app.auth_page.open()
    app.auth_page.go_to_register()
    app.register_page.fill_login(user.username)
    app.register_page.fill_password(user.password)
    app.register_page.fill_submut_password(user.password)
    app.register_page.submut()

    app.register_page.should_password_length_error_be_visible()


def test_registering_with_a_password_mismatch(in_browser):
    user = User.random()

    app.auth_page.open()
    app.auth_page.go_to_register()
    app.register_page.fill_login(user.username)
    app.register_page.fill_password(user.username)
    app.register_page.fill_submut_password(user.password)
    app.register_page.submut()

    app.register_page.should_password_mismatch_error_be_visible()


def test_registering_an_existing_user(in_browser, user):
    user = user

    app.auth_page.open()
    app.auth_page.go_to_register()
    app.register_page.fill_login(user.username)
    app.register_page.fill_password(user.password)
    app.register_page.fill_submut_password(user.password)
    app.register_page.submut()

    app.register_page.should_user_already_exists_error_be_visible(user.username)
