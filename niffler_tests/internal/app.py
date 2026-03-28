from internal.model.pages.register import RegisterPage
from internal.model.pages.spendings import SpendingsPage
from internal.model.pages.auth import AuthPage


class Application:
    def __init__(self) -> None:
        self.auth_page = AuthPage()
        self.spendings_page = SpendingsPage()
        self.register_page = RegisterPage()


system_under_test = Application()
