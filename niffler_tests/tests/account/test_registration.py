from selene import be, browser, have
from selene.support.shared.jquery_style import s

from niffler_tests.internal.models.user import fake


def test_registering_a_user(in_browser, as_a_random_user):
    user = as_a_random_user

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


def test_registering_with_a_short_username(in_browser, as_a_random_user):
    user = as_a_random_user

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


def test_registering_with_a_long_username(in_browser, as_a_random_user):
    user = as_a_random_user
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


def test_registering_with_a_short_password(in_browser, as_a_random_user):
    user = as_a_random_user

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


def test_registering_with_a_password_mismatch(in_browser, as_a_random_user):
    user = as_a_random_user

    browser.open("/")
    s(".form__register").click()
    register_form = s("#register-form")
    register_form.s("#username").type(user.login)
    register_form.s("#password").type(user.login)
    register_form.s("#passwordSubmit").type(user.password)
    register_form.s(".form__submit").click()

    s(".form__error").should(have.exact_text("Passwords should be equal"))


def test_registering_an_existing_user(in_browser, as_a_registered_user):
    user = as_a_registered_user

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
