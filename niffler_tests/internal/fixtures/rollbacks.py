from contextlib import contextmanager

import pytest


@pytest.fixture
def rollback_user(users_client):
    @contextmanager
    def _rollback(user):
        original = user.model_copy()
        yield user
        users_client.update_user(original)

    return _rollback

@pytest.fixture
def rollback_spends(spends_client):
    created_spends = []

    yield created_spends

    if created_spends:
        spend_ids = [spend.id for spend in created_spends]
        spends_client.delete_spends(spend_ids)
