from internal.app import system_under_test as app


def test_a_registered_user_logging_in(in_browser, as_a_registered_user):
    user = as_a_registered_user

    app.auth_page.open()
    app.auth_page.log_in(user.login, user.password)

    app.auth_page.should_be_logged()


def test_a_random_user_logging_in(in_browser, as_a_random_user):
    user = as_a_random_user

    app.auth_page.open()

    app.auth_page.fill_login(user.login)
    app.auth_page.fill_password(user.password)
    app.auth_page.submit()

    app.auth_page.should_display_invalid_credentials_message()


def test_logging_in_with_invalid_password(in_browser, as_a_registered_user):
    user = as_a_registered_user

    app.auth_page.open()

    app.auth_page.fill_login(user.login)
    app.auth_page.fill_password(user.login)
    app.auth_page.submit()

    app.auth_page.should_display_invalid_credentials_message()


def test_logging_out(in_browser, as_a_logged_user):
    _ = as_a_logged_user

    app.spendings_page.header.log_out()

    app.auth_page.should_be_not_logged()
