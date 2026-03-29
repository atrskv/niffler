from selene.support.shared.jquery_style import s, ss
from selene import have, be
from internal.utils import step


class CategoriesList:
    def __init__(self) -> None:
        self._s = s("form + .MuiGrid-container")
        self._categories = self._s.ss("form + .MuiGrid-item")

    def item(self, value):
        if isinstance(value, int):
            return CategoryItem(self.items[value - 1])
        elif isinstance(value, str):
            return CategoryItem(self.items.element_by(have.text(value)))

    @property
    def items(self):
        return self._categories

    @step
    def should_have_empty(self):
        self._categories.should(have.size(0))


class CategoryItem:
    def __init__(self, _s) -> None:
        self._s = _s
        self._alert = s(".MuiAlert-standardSuccess")

    @step
    def archive(self, timeout=30):
        self._s.s("[aria-label='Archive category']").click()

        s(".MuiPaper-root").wait.for_(be.visible)

        actions_menu = s(".MuiDialogActions-root")
        actions_menu.ss("button").second.with_(click_by_js=True).click()

        s(".MuiDialogActions-root").wait.for_(be.not_.visible)

        self._alert.with_(timeout=timeout).should(be.visible)
        self._alert.with_(timeout=timeout).should(be.hidden)

    @step
    def edit(self, name):
        self._s.s("[aria-label='Edit category']").click()
        ss("[name=category]").second.clear().type(name)
        s("[type=submit]").click()

        self._alert.with_(timeout=20).should(be.visible)
        self._alert.with_(timeout=40).should(be.hidden)
