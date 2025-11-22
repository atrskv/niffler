from selene import be, browser, have
from selene.support.shared.jquery_style import s

from niffler_tests.internal.models.user import User


def test_log_in_as_an_user(in_browser, registered_user):
    user = registered_user

    browser.open("/")
    log_in_form = s(".form")
    log_in_form.s("[name=username]").type(user.login)
    log_in_form.s("[name=password]").type(user.password)
    log_in_form.s(".form__submit").click()

    s("#stat").should(be.visible)
    s("#spendings").should(be.visible)


def test_log_in_as_a_nonexistent_user(in_browser):
    user = User.create_random()

    browser.open("/")
    log_in_form = s(".form")
    log_in_form.s("[name=username]").type(user.login)
    log_in_form.s("[name=password]").type(user.password)
    log_in_form.s(".form__submit").click()

    s(".form__error").should(
        have.exact_text("Неверные учетные данные пользователя")
    )


def test_log_in_with_an_invalid_password(in_browser, registered_user):
    user = registered_user

    browser.open("/")
    log_in_form = s(".form")
    log_in_form.s("[name=username]").type(user.login)
    log_in_form.s("[name=password]").type(user.login)
    log_in_form.s(".form__submit").click()

    s(".form__error").should(
        have.exact_text("Неверные учетные данные пользователя")
    )
