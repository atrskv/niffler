from datetime import date
from internal.app import system_under_test as app
from selene import be
from selene.support.shared.jquery_style import s
from internal.data.models import currency
from internal.data.models.currency import Currency
from internal.data.models.spend import SpendAddUI
from internal.data.models.user import fake
from internal.marks import pages


@pages.spending
def test_adding_a_new_spend(in_browser, spend_db, as_a_registered_user):
    user = as_a_registered_user
    spend = SpendAddUI.random()

    app.spendings_page.fill_amount(spend.amount)
    app.spendings_page.fill_currency(spend.currency.value)
    app.spendings_page.fill_category(spend.category)
    app.spendings_page.datepicker.fill_date_using_manual_input(spend.input_date)
    app.spendings_page.fill_description(spend.description)
    app.spendings_page.save()

    result = spend_db.get_spends_by_username(user.login)
    app.spendings_page.wait_for_alert()

    assert len(result) == 1
    assert user.login == result[0].username
    assert float(spend.amount) == result[0].amount
    assert spend.currency.name.upper() == result[0].currency
    assert spend.description == result[0].description


@pages.spending
def test_adding_a_new_category(in_browser, spend_db, as_a_registered_user):
    user = as_a_registered_user
    spend = SpendAddUI.random()

    app.spendings_page.fill_amount(spend.amount)
    app.spendings_page.fill_currency(spend.currency.value)
    app.spendings_page.fill_category(spend.category)
    app.spendings_page.datepicker.fill_date_using_manual_input(spend.input_date)
    app.spendings_page.fill_description(spend.description)
    app.spendings_page.save()

    app.spendings_page.wait_for_alert()
    result = spend_db.get_user_categories(user.login)

    assert len(result) == 1
    assert user.login == result[0].username
    assert result[0].name == spend.category
