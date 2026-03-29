from requests.exceptions import HTTPError
from internal.data.models.spend import SpendAddAPI
import pytest


class TestAdding:
    def test_add_spend(self, spends_client, user, rollback_spends, category):
        spend_data = SpendAddAPI.random(category_name=category.name)

        created = spends_client.add_spend(spend_data, user.username)

        assert created.amount == spend_data.amount
        assert created.description == spend_data.description
        assert created.currency == spend_data.currency
        rollback_spends.append(created)

    def test_add_spend_with_invalid_amount(self, spends_client, user):
        spend_data = SpendAddAPI.random()
        spend_data.amount = "abc"

        with pytest.raises(HTTPError) as e:
            spends_client.add_spend(spend_data, user.username)

        assert e.value.response.status_code == 400
        assert "Failed to read request" in e.value.response.text


class TestUpdating:
    def test_update_spend_already_deleted(self, spends_client, user, category):
        spend_data = SpendAddAPI.random(category_name=category.name)
        created = spends_client.add_spend(spend_data, user.username)
        new_amount = created.amount = 99.0

        spends_client.delete_spends([created.id])
        created.amount = new_amount
        with pytest.raises(Exception) as e:
            spends_client.edit_spend(created)

        assert e.value.response.status_code == 404
        assert "Can`t find spend by given id" in e.value.response.text

    def test_update_spend(self, spends_client, user, rollback_spends, category):
        spend_data = SpendAddAPI.random(category_name=category.name)
        created = spends_client.add_spend(spend_data, user.username)
        new_amount = created.amount = 99.0
        created.amount = new_amount

        edited = spends_client.edit_spend(created)

        assert edited.amount == new_amount
        assert edited.description == created.description
        assert edited.currency == created.currency
        rollback_spends.append(edited)


def test_delete_spend(spends_client, category,user):
    spend_data = SpendAddAPI.random(category_name=category.name)

    created = spends_client.add_spend(spend_data, user.username)
    spends_client.delete_spends([created.id])

    all_spends = spends_client.get_spends()
    assert not any(s.id == created.id for s in all_spends)
