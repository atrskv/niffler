from selene import browser
from selene.support.shared.jquery_style import s


class Header:
    def __init__(self) -> None:
        self._s = s("header")

    def open(self):
        browser.open("/")

    def log_out(self):
        self._s.s("[aria-label=Menu]").click()

        s(".MuiList-root").ss("li")[-1].click()
        s(".MuiDialogActions-root").ss("button").second.click()
