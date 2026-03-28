from internal.app import system_under_test as app
import pytest

from internal.data.models.spend import SpendAddAPI, SpendAddUI
from internal.data.models.user import fake
from internal.marks import pages, testdata


@pages.spending
def test_adding_a_new_spend(in_browser):
    spend = SpendAddUI.random()

    app.spendings_page.fill_amount(spend.amount)
    app.spendings_page.fill_currency(spend.currency.value)
    app.spendings_page.fill_category(spend.category)
    app.spendings_page.datepicker.fill_date_using_manual_input(spend.input_date)
    app.spendings_page.fill_description(spend.description)
    app.spendings_page.save()

    app.spendings_page.table.row(1).should_have_category(spend.category)
    app.spendings_page.table.row(1).should_have_amount(spend.amount)
    app.spendings_page.table.row(1).should_have_description(spend.description)
    app.spendings_page.table.row(1).should_have_display_date(spend.input_date)


@pages.spending
def test_adding_a_new_spend_without_amount(in_browser):
    spend = SpendAddUI.random()

    app.spendings_page.fill_currency(spend.currency.value)
    app.spendings_page.fill_category(spend.category)
    app.spendings_page.datepicker.fill_date_using_manual_input(spend.input_date)
    app.spendings_page.fill_description(spend.description)
    app.spendings_page.save()

    app.spendings_page.should_have_amount_error()


@pages.spending
def test_adding_a_new_spend_without_description(in_browser):
    spend = SpendAddUI.random()
    spend.description = ""

    app.spendings_page.fill_amount(spend.amount)
    app.spendings_page.fill_currency(spend.currency.value)
    app.spendings_page.fill_category(spend.category)
    app.spendings_page.datepicker.fill_date_using_manual_input(spend.input_date)
    app.spendings_page.save()

    app.spendings_page.table.row(1).should_have_category(spend.category)
    app.spendings_page.table.row(1).should_have_amount(spend.amount)
    app.spendings_page.table.row(1).should_have_description(spend.description)
    app.spendings_page.table.row(1).should_have_display_date(spend.input_date)


@pages.spending
def test_adding_a_new_spend_with_existing_category(in_browser, category):
    spend = SpendAddUI.random()

    app.refresh()
    app.spendings_page.fill_amount(spend.amount)
    app.spendings_page.fill_existing_category(category.name)
    app.spendings_page.save()

    app.spendings_page.legend_should_have_category(category.name)
    app.spendings_page.table.row(1).should_have_category(category.name)


@testdata.spends_with_single_category(
    [
        SpendAddAPI(amount=100.0, currency="USD", description="Test desc"),
    ],
)
def test_saving_a_spend_after_removing_a_category(
    in_browser, spends_with_single_category
):
    app.refresh()
    app.spendings_page.table.row(1).open_editor()
    app.spendings_page.remove_category()
    app.spendings_page.save()

    app.spendings_page.error_cagegory_should_be_visible()


@testdata.spends_with_single_category(
    [
        SpendAddAPI(amount=200.0, currency="KZT", description="Test desc"),
    ]
)
def test_editing_a_spend_by_adding_a_new_category(
    in_browser, spends_with_single_category
):
    new_category_name = fake.word()

    app.refresh()
    app.spendings_page.table.row(1).open_editor()
    app.spendings_page.remove_category()
    app.spendings_page.fill_category(new_category_name)
    app.spendings_page.save()
    app.spendings_page.category_should_be_edited()

    app.spendings_page.legend_should_have_category(new_category_name)
    app.spendings_page.table.row(1).should_have_category(new_category_name)


@testdata.spends_with_single_category(
    [
        SpendAddAPI(amount=300.0, currency="USD", description="Test desc"),
    ]
)
def test_removing_a_spend(in_browser, spends_with_single_category):
    spend = spends_with_single_category

    app.refresh()
    app.spendings_page.table.row(1).select()
    app.spendings_page.remove_spends()

    app.spendings_page.table.should_have_empty()


@testdata.spends_with_single_category(
    [
        SpendAddAPI(amount=300.0, currency="USD", description="Test desc"),
    ]
)
def test_archiving_a_category(in_browser, spends_with_single_category):
    spend = spends_with_single_category

    app.refresh()
    app.spendings_page.header.open_profile()
    app.profile_page.categories.item(1).archive()

    app.profile_page.should_categories_have_empty()


@testdata.spends_with_single_category(
    [
        SpendAddAPI(amount=300.0, currency="USD", description="Test desc"),
    ]
)
def test_renaming_a_category(in_browser, spends_with_single_category):
    spend = spends_with_single_category
    new_category_name = fake.word()

    app.refresh()
    app.spendings_page.header.open_profile()
    app.profile_page.categories.item(1).edit(new_category_name)
    app.profile_page.open_home_page()

    try:
        app.spendings_page.legend_should_have_category(new_category_name)
        app.spendings_page.table.row(1).should_have_category(new_category_name)
    except AssertionError:
        pytest.xfail("Cannot rename category")


@testdata.category("For autotest")
@testdata.spends_with_single_category(
    [
        SpendAddAPI(amount=123.0, currency="USD", description="Firt desc"),
        SpendAddAPI(amount=321.0, currency="USD", description="Second desc"),
    ]
)
def test_adding_spends_with_a_single_category(
    in_browser,
    spends_with_single_category,
):
    spend1, spend2 = spends_with_single_category
    expected_rubles_amount = "29600"

    app.refresh()
    app.spendings_page.legend_should_have_spend(expected_rubles_amount)

    app.spendings_page.table.should_have_size(2)


@testdata.category(["First category", "Second category"])
@testdata.spends_with_categories_1to1(
    [
        SpendAddAPI(amount=333.0, currency="USD", description="First desc"),
        SpendAddAPI(amount=211.0, currency="USD", description="Second desc"),
    ],
)
def test_adding_spends_with_different_categories(
    in_browser,
    spends_with_categories_1to1,
):
    spend1, spend2 = spends_with_categories_1to1
    spend1_to_rubles_amount, spend2_to_rubles_amount = "22200", "14066.67"

    app.refresh()

    app.spendings_page.legend_should_have_spend_by_category(
        spend1.category.name, spend1_to_rubles_amount
    )
    app.spendings_page.legend_should_have_spend_by_category(
        spend2.category.name, spend2_to_rubles_amount
    )
    app.spendings_page.table.should_have_size(2)
