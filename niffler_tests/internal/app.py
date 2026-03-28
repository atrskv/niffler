from internal.model.pages.home import HomePage
from internal.model.pages.profile import ProfilePage
from internal.model.pages.register import RegisterPage
from internal.model.pages.spendings import SpendingsPage
from internal.model.pages.auth import AuthPage
from selene import browser


class Application:
    def __init__(self) -> None:
        self.auth_page = AuthPage()
        self.home = HomePage()
        self.spendings_page = SpendingsPage()
        self.register_page = RegisterPage()
        self.profile_page = ProfilePage()

    def refresh(self):
        browser.driver.refresh()


system_under_test = Application()
