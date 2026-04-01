import allure
import pytest
from requests.exceptions import HTTPError


@allure.story("Adding")
class TestAdding:
    def test_add_spend(self, spends_client, as_a_registered_user, spend_payload):
        created_spend = spends_client.add_spend(
            spend_payload, as_a_registered_user.username
        )

        assert created_spend.amount == spend_payload.amount
        assert created_spend.description == spend_payload.description
        assert created_spend.currency == spend_payload.currency

    def test_add_spend_with_invalid_amount(
        self, spends_client, as_a_registered_user, spend_payload
    ):
        spend_payload.amount = "abc"

        with pytest.raises(HTTPError) as e:
            spends_client.add_spend(spend_payload, as_a_registered_user.username)

        assert e.value.response.status_code == 400
        assert "Failed to read request" in e.value.response.text


@allure.story("Updating")
class TestUpdating:
    def test_update_spend_already_deleted(
        self, spends_client, as_a_registered_user, created_spend
    ):
        spends_client.delete_spends([created_spend.id])
        created_spend.amount = 99.0

        with pytest.raises(HTTPError) as e:
            spends_client.edit_spend(created_spend)

        assert e.value.response.status_code == 404
        assert "Can`t find spend by given id" in e.value.response.text

    def test_update_spend_amount_and_preserve_fields(
        self, spends_client, created_spend
    ):
        expected_amount = 99.0
        created_spend.amount = expected_amount

        updated_spend = spends_client.edit_spend(created_spend)

        assert updated_spend.amount == expected_amount
        assert updated_spend.description == created_spend.description
        assert updated_spend.currency == created_spend.currency


@allure.story("Deleting")
class TestDeleting:
    def test_delete_spend(self, spends_client, created_spend):
        spends_client.delete_spends([created_spend.id])

        all_spends = spends_client.get_spends()

        assert not any(s.id == created_spend.id for s in all_spends)


pytestmark = [
    pytest.mark.allure_label("API: Spends and users", label_type="epic"),
    pytest.mark.allure_label("Spends", label_type="feature"),
]
