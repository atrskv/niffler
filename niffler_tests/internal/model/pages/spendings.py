from selene import browser, have, be
from selene.support.shared.jquery_style import s
from internal.model.components.datepicker import Datepicker
from internal.model.components.header import Header
from internal.model.components.spendings_table import SpendingsTable
from selenium.webdriver import Keys
import sys


class SpendingsPage:
    def __init__(self) -> None:
        self.header = Header()
        self.datepicker = Datepicker()
        self.table = SpendingsTable()
        self._legend = s("#legend-container")
        self._category = s("#category")
        self._alert = s(".MuiAlert-standardSuccess")

    def open(self):
        browser.open("/main")

    def fill_amount(self, value):
        s("#amount").set_value(value)

    def fill_currency(self, value):
        s("#currency").click()
        s("[role=listbox]").ss("li")[value].click()

    def fill_category(self, value):
        self._category.type(value)

    def fill_existing_category(self, value):
        s("#category + ul").ss("li").element_by(have.text(value)).click()

    def fill_description(self, value):
        s("#description").type(value)

    def remove_category(self):
        self._category.click()
        self._category.send_keys(
            Keys.COMMAND if sys.platform == "darwin" else Keys.CONTROL,
            "a",
        )
        self._category.send_keys(Keys.DELETE)

    def remove_spends(self):
        s("#delete").click()
        modal = s(".MuiDialogActions-root")
        modal.ss("button").second.click()
        modal.wait.for_(be.not_.visible)

    def save(self):
        s("#save").click()

    def error_cagegory_should_be_visible(self):
        s(".input__helper-text").should(have.exact_text("Please choose category"))

    def legend_should_have_category(self, value):
        self._legend_should_have_text(value)

    def legend_should_have_spend(self, value):
        self._legend_should_have_text(value)

    def _legend_should_have_text(self, value):
        self._legend.ss("li").by(have.text(value)).should(have.size(1))

    def legend_should_have_spend_by_category(self, category, spend):
        self._legend.s("ul").ss("li").by(have.text(category)).first.should(
            have.text(spend)
        )

    def should_have_amount_error(self):
        s(".input__helper-text").should(
            have.exact_text("Amount has to be not less then 0.01")
        )

    def wait_for_alert(self, timeout=20):
        self._alert.with_(timeout=timeout).wait.for_(be.visible)
        self._alert.with_(timeout=timeout).wait.for_(be.hidden)

    def category_should_be_edited(self, timeout=20):
        self.wait_for_alert(timeout)
