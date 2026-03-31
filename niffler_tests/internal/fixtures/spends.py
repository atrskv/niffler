import pytest

import random

from internal.clients.api.spends import SpendsService
from internal.data.models.user import fake
from internal.data.models.spend import CategoryAPI, SpendAddAPI
from internal.data.models.currency import Currency
from internal.utils.common import random_recent_days


@pytest.fixture
def category(
    request, spends_client: SpendsService, spend_db
) -> CategoryAPI | list[CategoryAPI]:
    if hasattr(request, "param"):
        param = request.param
        if isinstance(param, list):
            names = param
        elif isinstance(param, str):
            names = [param]
        else:
            names = [fake.word()]
    else:
        names = [fake.word()]

    existing_categories = spends_client.get_categories()

    result = []

    for name in names:
        existing = next(
            (c for c in existing_categories if c.name.lower() == name.lower()), None
        )
        if existing:
            result.append(existing)
        else:

            if len(name) < 2:
                name = name + "a"

            created = spends_client.add_category(name)
            result.append(created)
            existing_categories.append(created)

    yield result if len(result) > 1 else result[0]

    categories = result if isinstance(result, list) else [result]

    for c in categories:
        spend_db.delete_spends_by_category_id(c.id)
        spend_db.delete_category_by_id(c.id)


@pytest.fixture
def spends_with_single_category(
    request, spends_client, category: CategoryAPI, as_a_logged_user
):
    user = as_a_logged_user
    spends_params = getattr(
        request,
        "param",
        [
            SpendAddAPI(
                amount=float(fake.random_int(min=10, max=100)),
                currency=random.choice(list(Currency)).name.upper(),
                description=fake.sentence(),
                category=category.name,
            )
        ],
    )

    spends = []

    for spend in spends_params:
        if spend.category is None:
            spend.category = category.name
        spend.spendDate = random_recent_days(60).date().isoformat()
        created = spends_client.add_spend(spend, username=user.username)
        spends.append(created)

    return spends


@pytest.fixture
def spends_with_categories_1to1(as_a_logged_user, request, spends_client, category):
    user = as_a_logged_user
    categories = category if isinstance(category, list) else [category]
    spends_params = getattr(request, "param", [])

    spends = []
    for c, spend in zip(categories, spends_params):
        spend.category = c.name
        spend.spendDate = random_recent_days(60).isoformat()
        created = spends_client.add_spend(spend, username=user.username)
        spends.append(created)

    return spends
