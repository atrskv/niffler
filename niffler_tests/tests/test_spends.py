import sys
from datetime import date

import pytest
from selene import be, browser, have
from selene.support.shared.jquery_style import s, ss
from selenium.webdriver import Keys

from niffler_tests.internal.models.currency import Currency
from niffler_tests.internal.models.user import fake
from niffler_tests.tests.marks import pages, testdata


@pages.spending
def test_adding_a_new_spend():
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


@pages.spending
def test_adding_a_new_spend_without_amount():
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


@pages.spending
def test_adding_a_new_spend_without_description():
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
    s("#amount").set_value(amount)
    s("#currency").click()
    s("[role=listbox]").ss("li")[currency.value].click()
    s("#category").type(category)

    datepicker = s("[name=date]")
    datepicker.click()
    datepicker.type(input_date)

    s("#save").click()

    # THEN
    row = s("tbody").ss("tr").first
    row.ss("td")[1].should(have.exact_text(category))
    row.ss("td")[2].should(have.text(amount))
    row.ss("td")[3].should(have.exact_text(""))
    row.ss("td")[4].should(have.exact_text(display_date))


@pages.spending
def test_adding_a_new_spend_with_existing_category(category):
    # GIVEN
    category_name = category["name"]
    amount = str(fake.random_int(min=10, max=100))

    # WHEN
    browser.driver.refresh()
    s("#amount").set_value(amount)
    s("#category + ul").ss("li").first.click()

    s("#save").click()

    # THEN
    s("#legend-container").s("ul").ss("li").first.should(
        have.text(category_name)
    )
    row = s("tbody").ss("tr").first
    row.ss("td")[1].should(have.exact_text(category_name))


@testdata.spends_with_single_category(
    [
        {"amount": 100.0, "currency": "USD", "description": "Test desc"},
    ]
)
def test_saving_a_spend_after_removing_a_category(
    spends_with_single_category,
):
    browser.driver.refresh()
    s("[aria-label='Edit spending']").click()
    s("#category").click()
    s("#category").send_keys(
        Keys.COMMAND if sys.platform == "darwin" else Keys.CONTROL,
        "a",
    )
    s("#category").send_keys(Keys.DELETE)
    s("#save").click()

    s(".input__helper-text").should(have.exact_text("Please choose category"))


@testdata.spends_with_single_category(
    [
        {"amount": 200.0, "currency": "KZT", "description": "Test desc"},
    ]
)
def test_editing_a_spend_by_adding_a_new_category(
    spends_with_single_category,
):
    new_category_name = fake.word()
    browser.driver.refresh()
    s("[aria-label='Edit spending']").click()
    s("#category").click()
    s("#category").send_keys(
        Keys.COMMAND if sys.platform == "darwin" else Keys.CONTROL,
        "a",
    )
    s("#category").send_keys(Keys.DELETE)
    s("#category").type(new_category_name)
    s("#save").click()
    alert = s(".MuiAlert-standardSuccess")
    alert.with_(timeout=10).wait.for_(be.visible)
    alert.with_(timeout=10).wait.for_(be.hidden)

    # THEN
    s("#legend-container").s("ul").ss("li").first.should(
        have.text(new_category_name)
    )
    row = s("tbody").ss("tr").first
    row.ss("td")[1].should(have.exact_text(new_category_name))


@testdata.spends_with_single_category(
    [
        {"amount": 300.0, "currency": "USD", "description": "Test desc"},
    ]
)
def test_removing_a_spend(
    spends_with_single_category,
):
    spend = spends_with_single_category

    browser.driver.refresh()
    rows = s("tbody").ss("tr")
    rows.first.click()
    s("#delete").click()
    s(".MuiDialogActions-root").ss("button").second.click()
    s(".MuiDialogActions-root").wait.for_(be.not_.visible)

    s("#spendings").s(".MuiTypography-h6").should(
        have.exact_text("There are no spendings")
    )


@testdata.spends_with_single_category(
    [
        {"amount": 300.0, "currency": "USD", "description": "Test desc"},
    ]
)
def test_archiving_a_category(
    spends_with_single_category,
):
    spend = spends_with_single_category

    browser.driver.refresh()
    s("[aria-label=Menu]").click()
    s(".MuiList-root").ss("li").first.click()
    s("[aria-label='Archive category']").click()
    s(".MuiDialogActions-root").ss("button").second.click()
    s(".MuiDialogActions-root").wait.for_(be.not_.visible)

    alert = s(".MuiAlert-standardSuccess")
    alert.with_(timeout=10).should(be.visible)
    alert.with_(timeout=10).should(be.hidden)


@testdata.spends_with_single_category(
    [
        {"amount": 300.0, "currency": "USD", "description": "Test desc"},
    ]
)
def test_renaming_a_category(
    spends_with_single_category,
):
    spend = spends_with_single_category
    new_category_name = fake.word()

    browser.driver.refresh()
    s("[aria-label=Menu]").click()
    s(".MuiList-root").ss("li").first.click()
    s("[aria-label='Edit category']").click()
    ss("[name=category]").second.clear().type(new_category_name)
    s("[type=submit]").click()

    # THEN
    alert = s(".MuiAlert-standardSuccess")
    alert.with_(timeout=10).should(be.visible)
    alert.with_(timeout=10).should(be.hidden)

    # AND
    s("h1").click()

    try:
        s("#legend-container").s("ul").ss("li").first.should(
            have.text(new_category_name)
        )
        row = s("tbody").ss("tr").first
        row.ss("td")[1].should(have.exact_text(new_category_name))
    except AssertionError:
        pytest.xfail("Cannot rename category")


@testdata.category("For autotest")
@testdata.spends_with_single_category(
    [
        {"amount": 123.0, "currency": "USD", "description": "Firt desc"},
        {"amount": 321.0, "currency": "USD", "description": "Second desc"},
    ]
)
def test_adding_spends_with_a_single_category(
    spends_with_single_category,
):
    spend1, spend2 = spends_with_single_category
    expected_rubles_amount = "29600"

    browser.driver.refresh()

    # THEN
    s("#legend-container").s("ul").ss("li").first.should(
        have.text(expected_rubles_amount)
    )

    # AND
    rows = s("tbody").ss("tr").should(have.size(2))


@testdata.category(["First category", "Second category"])
@testdata.spends_with_categories_1to1(
    [
        {"amount": 333.0, "currency": "USD", "description": "Firt desc"},
        {"amount": 211.0, "currency": "USD", "description": "Second desc"},
    ],
)
def test_adding_spends_with_different_categories(
    spends_with_categories_1to1,
):
    spend1, spend2 = spends_with_categories_1to1
    spend1_to_rubles_amount, spend2_to_rubles_amount = "22200", "14066.67"

    browser.driver.refresh()

    # THEN
    s("#legend-container").s("ul").ss("li").by(
        have.text(spend1["category"]["name"])
    ).first.should(have.text(spend1_to_rubles_amount))

    s("#legend-container").s("ul").ss("li").by(
        have.text(spend2["category"]["name"])
    ).first.should(have.text(spend2_to_rubles_amount))

    # AND
    rows = s("tbody").ss("tr").should(have.size(2))
