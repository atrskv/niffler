from datetime import date

from selene import have
from selene.support.shared.jquery_style import s, ss

from niffler_tests.internal.models.currency import Currency
from niffler_tests.internal.models.user import fake


def test_add_a_new_spending(in_browser, as_logged_user):
    # GIVEN
    amount = str(fake.random_int(min=10, max=100))
    currency = fake.random_element(list(Currency))
    category = fake.word()
    random_date = fake.date_between(
        start_date=date(2000, 1, 1), end_date=date.today()
    )
    input_date = random_date.strftime("%m/%d/%Y")
    display_date = random_date.strftime("%b %d, %Y")
    description = fake.sentence()

    # WHEN
    new_spending_button = ss("a").second
    new_spending_button.click()

    s("#amount").set_value(amount)
    s("#currency").click()
    s("[role=listbox]").ss("li")[currency.value].click()
    s("#category").type(category)

    datepicker = s("[name=date]")
    datepicker.click()
    datepicker.type(input_date)

    s("#description").type(description)
    s("#save").click()

    # THEN
    row = s("tbody").ss("tr").first
    row.ss("td")[1].should(have.exact_text(category))
    row.ss("td")[2].should(have.text(amount))
    row.ss("td")[3].should(have.exact_text(description))
    row.ss("td")[4].should(have.exact_text(display_date))


def test_add_a_new_spending_without_amount(in_browser, as_logged_user):
    # GIVEN
    currency = fake.random_element(list(Currency))
    category = fake.word()
    random_date = fake.date_between(
        start_date=date(2000, 1, 1), end_date=date.today()
    )
    input_date = random_date.strftime("%m/%d/%Y")
    display_date = random_date.strftime("%b %d, %Y")
    description = fake.sentence()

    # WHEN
    new_spending_button = ss("a").second
    new_spending_button.click()

    s("#currency").click()
    s("[role=listbox]").ss("li")[currency.value].click()
    s("#category").type(category)

    datepicker = s("[name=date]")
    datepicker.click()
    datepicker.type(input_date)

    s("#description").type(description)
    s("#save").click()

    # THEN
    s(".input__helper-text").should(
        have.exact_text("Amount has to be not less then 0.01")
    )
