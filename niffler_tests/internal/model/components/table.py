from selene.support.shared.jquery_style import s
from selene import have


class Table:
    def __init__(self) -> None:
        self._body = s("tbody")
        self._rows = self._body.ss("tr")

    def row(self, value):
        if isinstance(value, int):
            return self._rows[value - 1]
        elif isinstance(value, str):
            return self._rows.element_by(have.text(value))

    @property
    def rows(self):
        return self._rows
