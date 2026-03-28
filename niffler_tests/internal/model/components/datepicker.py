from selene.support.shared.jquery_style import s
from internal.utils import step


class Datepicker:
    def __init__(self) -> None:
        self._input = s("[name=date")

    @step
    def fill_date_using_manual_input(self, dt):
        self._input.click()
        self._input.type(dt.strftime("%m/%d/%Y"))
