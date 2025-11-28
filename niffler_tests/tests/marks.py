import pytest


class pages:
    spending = pytest.mark.usefixtures("spending_page")


class testdata:
    category = lambda c: pytest.mark.parametrize(
        "category",
        [c],
        indirect=True,
    )

    spends_with_single_category = lambda s: pytest.mark.parametrize(
        "spends_with_single_category", [s], indirect=True
    )
    spends_with_categories_1to1 = lambda s: pytest.mark.parametrize(
        "spends_with_categories_1to1",
        [s],
        indirect=True,
    )
