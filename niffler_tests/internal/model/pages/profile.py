from selene import browser
from selene.support.shared.jquery_style import s

from internal.model.components.categories_list import CategoriesList


class ProfilePage:
    def __init__(self) -> None:

        self.categories = CategoriesList()

    def open(self):
        browser.open("/profile")

    def open_home_page(self):
        s("h1").click()

    def should_categories_have_empty(self):
        self.categories.should_have_empty()
