import allure
import pytest
from requests import HTTPError


@allure.story("Getting")
class TestGetting:
    def test_get_current_user(self, users_client):
        current_user = users_client.get_current_user()

        assert current_user.id is not None
        assert current_user.username is not None

    def test_get_all_users(self, users_client):
        users = users_client.get_all_users()

        assert isinstance(users, list)

        user_ids = [user.id for user in users]
        assert len(user_ids) == len(set(user_ids))

    def test_get_all_users_unauthorized(self, users_client):
        users_client.session.headers.pop("Authorization", None)

        with pytest.raises(HTTPError) as e:
            users_client.get_all_users()

        assert e.value.response.status_code == 401


@allure.story("Searching")
class TestSearching:
    def test_search_users_not_found(self, users_client):
        search_query = "nonexistent_user_12345"

        users = users_client.get_all_users(search_query=search_query)

        assert users == []


@allure.story("Updating")
class TestUpdating:
    def test_update_user(self, users_client, created_user):
        expected_fullname = "New Fullname"
        created_user.fullname = expected_fullname

        updated_user = users_client.update_user(created_user)

        assert updated_user.fullname == expected_fullname

    def test_update_user_too_long_firstname(self, users_client, created_user):
        created_user.firstname = "A" * 31

        with pytest.raises(HTTPError) as e:
            users_client.update_user(created_user)

        assert e.value.response.status_code == 400
        assert "First name can`t be longer than 30 characters" in e.value.response.text


pytestmark = [
    pytest.mark.allure_label("API: Spends and users", label_type="epic"),
    pytest.mark.allure_label("Users", label_type="feature"),
]
