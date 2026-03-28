from internal.model.components.table import Table
from selene import have
from selene.support.shared.jquery_style import s


class SpendingsTable:
    def __init__(self) -> None:
        self._table = Table()

    def row(self, value):
        if isinstance(value, int):
            return SpendingsTableRow(self._table._rows[value - 1])
        elif isinstance(value, str):
            return SpendingsTableRow(self._table._rows.element_by(have.text(value)))

    @property
    def rows(self):
        return self._table.rows

    def should_have_empty(self):
        s("#spendings").s(".MuiTypography-h6").should(
            have.exact_text("There are no spendings")
        )

    def should_have_size(self, value):
        self.rows.should(have.size(value))


class SpendingsTableRow:
    def __init__(self, _s) -> None:
        self._s = _s
        self._columns = self._s.ss("td")

    def open_editor(self):
        self._s.s("[aria-label='Edit spending']").click()

    def select(self):
        self._s.click()

    def should_have_category(self, value):
        self._columns.element(1).should(have.exact_text(value))

    def should_have_amount(self, value):
        self._columns.element(2).should(have.text(value))

    def should_have_description(self, value):
        self._columns.element(3).should(have.exact_text(value))

    def should_have_display_date(self, dt):
        self._columns.element(4).should(have.exact_text(dt.strftime("%b %d, %Y")))
