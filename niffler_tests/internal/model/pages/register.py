from selene import browser
from selene.support.shared.jquery_style import s
from selene import be, have
from internal.utils import step


class RegisterPage:
    def __init__(self) -> None:
        self._form = s("#register-form")
        self._error_form = s(".form__error")

    @step
    def open(self):
        browser.open("/")

    @step
    def fill_login(self, value):
        input = self._form.s("#username")
        input.type(value)

    @step
    def fill_password(self, value):
        input = self._form.s("#password")
        input.type(value)

    @step
    def fill_submut_password(self, value):
        self._form.s("#passwordSubmit").type(value)

    @step
    def submut(self):
        self._form.s(".form__submit").click()

    @step
    def register(self, login, password):
        self.fill_login(login)
        self.fill_password(password)
        self.fill_submut_password(password)
        self.submut()

    @step
    def should_login_length_error_be_visible(self):
        self._error_form.should(
            have.exact_text("Allowed username length should be from 3 to 50 characters")
        )

    @step
    def should_password_length_error_be_visible(self):
        self._error_form.should(
            have.exact_text("Allowed password length should be from 3 to 12 characters")
        )

    @step
    def should_user_already_exists_error_be_visible(self, login):
        self._error_form.should(have.exact_text(f"Username `{login}` already exists"))

    @step
    def should_password_mismatch_error_be_visible(self):
        self._error_form.should(have.text("Passwords should be equal"))

    @step
    def should_be_registered(self):
        s(".form__paragraph_success").should(
            have.exact_text("Congratulations! You've registered!")
        )
        s(".form_sign-in").should(be.visible)
