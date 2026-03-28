from selene.support.shared.jquery_style import s


class Header:
    def __init__(self) -> None:
        self._s = s("header")
        self._menu = s("[aria-label=Menu]")

    def open_profile(self):
        self._menu.click()
        s(".MuiList-root").ss("li").first.click()

    def log_out(self):
        self._menu.click()
        s(".MuiList-root").ss("li")[-1].click()
        s(".MuiDialogActions-root").ss("button").second.click()
