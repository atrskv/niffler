from internal.app import system_under_test as app
from internal.data.models.spend import SpendAddUI
from internal.marks import pages
import pytest


pytestmark = [
    pytest.mark.allure_label("Spends and categories", label_type="epic"),
    pytest.mark.allure_label("Categories", label_type="story"),
]

import polling2



@pages.spending
def test_adding_a_new_spend(spend_db, as_a_logged_user):
    user = as_a_logged_user
    spend = SpendAddUI.random()

    app.spendings_page.fill_amount(spend.amount)
    app.spendings_page.fill_currency(spend.currency.value)
    app.spendings_page.fill_category(spend.category)
    app.spendings_page.datepicker.fill_date_using_manual_input(spend.input_date)
    app.spendings_page.fill_description(spend.description)
    app.spendings_page.save()

    app.spendings_page.wait_for_alert()

    def _get_spends():
        return spend_db.get_spends_by_username(user.username)

    result = polling2.poll(
        target=_get_spends,
        check_success=lambda rows: len(rows) >= 1,
        step=0.5,
        timeout=10.0,
    )
    assert len(result) == 1
    assert user.username == result[0].username
    assert float(spend.amount) == result[0].amount
    assert spend.currency.name.upper() == result[0].currency
    assert spend.description == result[0].description


@pages.spending
def test_adding_a_new_category(spend_db, as_a_logged_user):
    user = as_a_logged_user
    spend = SpendAddUI.random()

    app.spendings_page.fill_amount(spend.amount)
    app.spendings_page.fill_currency(spend.currency.value)
    app.spendings_page.fill_category(spend.category)
    app.spendings_page.datepicker.fill_date_using_manual_input(spend.input_date)
    app.spendings_page.fill_description(spend.description)
    app.spendings_page.save()

    app.spendings_page.wait_for_alert()

    def _get_categories():
        return spend_db.get_user_categories(user.username)

    result = polling2.poll(
        target=_get_categories,
        check_success=lambda rows: len(rows) >= 1,
        step=0.5,
        timeout=10.0,
    )
    assert len(result) == 1
    assert user.username == result[0].username
    assert result[0].name == spend.category