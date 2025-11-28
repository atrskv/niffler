from selene import be, browser, have
from selene.support.shared.jquery_style import s


def test_a_registered_user_logging_in(in_browser, as_a_registered_user):
    user = as_a_registered_user

    browser.open("/")
    log_in_form = s(".form")
    log_in_form.s("[name=username]").type(user.login)
    log_in_form.s("[name=password]").type(user.password)
    log_in_form.s(".form__submit").click()

    s("#stat").should(be.visible)
    s("#spendings").should(be.visible)


def test_a_random_user_logging_in(in_browser, as_a_random_user):
    user = as_a_random_user

    browser.open("/")
    
    log_in_form = s(".form")
    log_in_form.wait.for_(be.visible)
    log_in_form.s("[name=username]").type(user.login)
    log_in_form.s("[name=password]").type(user.password)
    log_in_form.s(".form__submit").click()

    s(".form__error").should(
        have.exact_text("Неверные учетные данные пользователя")
    )


def test_logging_in_with_invalid_password(in_browser, as_a_registered_user):
    user = as_a_registered_user

    browser.open("/")
    log_in_form = s(".form")
    log_in_form.s("[name=username]").type(user.login)
    log_in_form.s("[name=password]").type(user.login)
    log_in_form.s(".form__submit").click()

    s(".form__error").should(
        have.exact_text("Неверные учетные данные пользователя")
    )


def test_logging_out(in_browser, as_a_logged_user):
    user = as_a_logged_user

    s("[aria-label=Menu]").click()
    s(".MuiList-root").ss("li")[-1].click()
    s(".MuiDialogActions-root").ss("button").second.click()

    s(".header").should(have.exact_text("Log in"))
    s(".form__register").should(have.exact_text("Create new account"))
