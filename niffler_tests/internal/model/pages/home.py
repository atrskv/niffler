from selene import browser
from internal.model.components.header import Header
from internal.utils import step


class HomePage:
    def __init__(self) -> None:
        self.header = Header()

    @step
    def open(self):
        browser.open("/main")
