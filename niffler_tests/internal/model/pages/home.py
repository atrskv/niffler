from selene import browser

from internal.model.components.header import Header


class HomePage:
    def __init__(self) -> None:
        self.header = Header()

    def open(self):
        browser.open("/main")
