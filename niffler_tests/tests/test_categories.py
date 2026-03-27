from datetime import date

from selene import be
from selene.support.shared.jquery_style import s
from internal.models.currency import Currency
from internal.models.user import fake
from internal.marks import pages


@pages.spending
def test_adding_a_new_spend(in_browser, spend_db, as_a_registered_user):
    # GIVEN
    amount = str(fake.random_int(min=10, max=100))
    currency = fake.random_element(list(Currency))
    category_name = fake.word()
    random_date = fake.date_between(start_date=date(2000, 1, 1), end_date=date.today())
    input_date = random_date.strftime("%m/%d/%Y")
    description = fake.sentence()
    user = as_a_registered_user

    # WHEN
    s("#amount").set_value(amount)
    s("#currency").click()
    s("[role=listbox]").ss("li")[currency.value].click()
    s("#category").type(category_name)

    datepicker = s("[name=date]")
    datepicker.click()
    datepicker.type(input_date)

    s("#description").type(description)
    s("#save").click()

    s(".MuiLoadingButton-loading").with_(timeout=60).wait.for_(be.not_.visible)

    # THEN
    result = spend_db.get_spends_by_username(user.login)
    assert len(result) == 1
    assert user.login == result[0].username
    assert float(amount) == result[0].amount
    assert currency.name.upper() == result[0].currency
    assert description == result[0].description


@pages.spending
def test_adding_a_new_category(in_browser, spend_db, as_a_registered_user):
    # GIVEN
    amount = str(fake.random_int(min=10, max=100))
    currency = fake.random_element(list(Currency))
    category_name = fake.word()
    random_date = fake.date_between(start_date=date(2000, 1, 1), end_date=date.today())
    input_date = random_date.strftime("%m/%d/%Y")
    description = fake.sentence()
    user = as_a_registered_user

    # WHEN
    s("#amount").set_value(amount)
    s("#currency").click()
    s("[role=listbox]").ss("li")[currency.value].click()
    s("#category").type(category_name).press_enter()

    datepicker = s("[name=date]")
    datepicker.click()
    datepicker.type(input_date)

    s("#description").type(description)
    s("#save").click()

    s(".MuiLoadingButton-loading").with_(timeout=60).wait.for_(be.not_.visible)

    # THEN
    result = spend_db.get_user_categories(user.login)
    assert len(result) == 1
    assert user.login == result[0].username
    assert result[0].name == category_name
