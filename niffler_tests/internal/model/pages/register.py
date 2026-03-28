from selene import browser
from selene.support.shared.jquery_style import s
from selene import be, have


class RegisterPage:
    def __init__(self) -> None:
        self._form = s("#register-form")
        self._error_form = s(".form__error")

    def open(self):
        browser.open("/")

    def fill_login(self, value):
        self._form.s("#username").type(value)

    def fill_password(self, value):
        self._form.s("#password").type(value)

    def fill_submut_password(self, value):
        self._form.s("#passwordSubmit").type(value)

    def submut(self):
        self._form.s(".form__submit").click()

    def register(self, login, password):
        self.fill_login(login)
        self.fill_password(password)
        self.fill_submut_password(password)
        self.submut()

    def should_login_length_error_be_visible(self):
        self._error_form.should(
            have.exact_text("Allowed username length should be from 3 to 50 characters")
        )

    def should_password_length_error_be_visible(self):
        self._error_form.should(
            have.exact_text("Allowed password length should be from 3 to 12 characters")
        )

    def should_user_already_exists_error_be_visible(self, login):
        self._error_form.should(have.exact_text(f"Username `{login}` already exists"))

    def should_password_mismatch_error_be_visible(self):
        self._error_form.should(have.exact_text("Passwords should be equal"))

    def should_be_registered(self):
        s(".form__paragraph_success").should(
            have.exact_text("Congratulations! You've registered!")
        )
        s(".form_sign-in").should(be.visible)
