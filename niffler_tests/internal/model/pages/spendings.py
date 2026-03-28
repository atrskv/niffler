from selene import browser

from internal.model.components.header import Header


class SpendingsPage:
    def __init__(self) -> None:
        self.header = Header()

    def open(self):
        browser.open("/main")
