from selene import be, browser, have
from selene.support.shared.jquery_style import s

from niffler_tests.internal.models.user import User, fake


def test_register_an_user(in_browser):
    user = User.create_random()

    browser.open("/")
    s(".form__register").click()
    register_form = s("#register-form")
    register_form.s("#username").type(user.login)
    register_form.s("#password").type(user.password)
    register_form.s("#passwordSubmit").type(user.password)
    register_form.s(".form__submit").click()

    s(".form__paragraph_success").should(
        have.exact_text("Congratulations! You've registered!")
    )
    s(".form_sign-in").should(be.visible)


def test_register_an_user_with_a_short_username(in_browser):
    user = User.create_random()

    browser.open("/")
    s(".form__register").click()
    register_form = s("#register-form")
    register_form.s("#username").type(user.login[:2])
    register_form.s("#password").type(user.password)
    register_form.s("#passwordSubmit").type(user.password)
    register_form.s(".form__submit").click()

    s(".form__error").should(
        have.exact_text(
            "Allowed username length should be from 3 to 50 characters"
        )
    )


def test_register_an_user_with_a_long_username(in_browser):
    user = User.create_random()
    user.login = fake.pystr(min_chars=51, max_chars=51)

    browser.open("/")
    s(".form__register").click()
    register_form = s("#register-form")
    register_form.s("#username").type(user.login)
    register_form.s("#password").type(user.password)
    register_form.s("#passwordSubmit").type(user.password)
    register_form.s(".form__submit").click()

    s(".form__error").should(
        have.exact_text(
            "Allowed username length should be from 3 to 50 characters"
        )
    )


def test_register_an_user_with_a_short_password(in_browser):
    user = User.create_random()

    browser.open("/")
    s(".form__register").click()
    register_form = s("#register-form")
    register_form.s("#username").type(user.login)
    register_form.s("#password").type(user.password[:2])
    register_form.s("#passwordSubmit").type(user.password[:2])
    register_form.s(".form__submit").click()

    s(".form__error").should(
        have.exact_text(
            "Allowed password length should be from 3 to 12 characters"
        )
    )


def test_register_an_user_with_a_password_mismatch(in_browser):
    user = User.create_random()

    browser.open("/")
    s(".form__register").click()
    register_form = s("#register-form")
    register_form.s("#username").type(user.login)
    register_form.s("#password").type(user.login)
    register_form.s("#passwordSubmit").type(user.password)
    register_form.s(".form__submit").click()

    s(".form__error").should(have.exact_text("Passwords should be equal"))


def test_register_an_user_that_already_exists(in_browser, registered_user):
    user = registered_user

    browser.open("/")
    s(".form__register").click()
    register_form = s("#register-form")
    register_form.s("#username").type(user.login)
    register_form.s("#password").type(user.password)
    register_form.s("#passwordSubmit").type(user.password)
    register_form.s(".form__submit").click()

    s(".form__error").should(
        have.exact_text(f"Username `{user.login}` already exists")
    )
