import pytest


@pytest.fixture
def rollback_user(users_client, as_a_registered_user):
    original = as_a_registered_user.model_copy()

    yield

    users_client.update_user(original)


@pytest.fixture
def rollback_spends(spends_client):
    created_spends = []

    yield created_spends

    if created_spends:
        spend_ids = [spend.id for spend in created_spends]
        spends_client.delete_spends(spend_ids)
