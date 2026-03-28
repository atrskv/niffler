from selene import browser
from selene.support.shared.jquery_style import s
from selene import be, have
from internal.utils import step


class AuthPage:
    def __init__(self) -> None:
        self._form = s(".form")
        self._error_form = s(".form__error")

    @step
    def open(self):
        browser.open("/")

    @step
    def go_to_register(self):
        s(".form__register").click()

    @step
    def fill_login(self, value):
        self._form.s("[name=username]").type(value)

    @step
    def fill_password(self, value):
        self._form.s("[name=password]").type(value)

    @step
    def submit(self):
        self._form.s(".form__submit").click()

    @step
    def log_in(self, login, password):
        self.fill_login(login)
        self.fill_password(password)
        self.submit()

    @step
    def should_be_logged(self):
        s("#stat").should(be.visible)
        s("#spendings").should(be.visible)

    @step
    def should_be_not_logged(self):
        s(".header").should(have.exact_text("Log in"))
        s(".form__register").should(have.exact_text("Create new account"))

    @step
    def should_display_invalid_credentials_message(self):
        self._error_form.should(have.exact_text("Неверные учетные данные пользователя"))
