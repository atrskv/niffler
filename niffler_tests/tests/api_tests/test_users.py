import pytest
from requests import HTTPError


class TestGetting:
    def test_get_current_user(self, users_client):
        user = users_client.get_current_user()

        assert user.id is not None
        assert user.username is not None

    def test_get_all_users(self, users_client):
        users = users_client.get_all_users()

        assert isinstance(users, list)
        ids = [u.id for u in users]
        assert len(ids) == len(set(ids))

    def test_get_all_users_unauthorized(self, users_client):
        users_client.session.headers.pop("Authorization", None)

        with pytest.raises(Exception) as e:
            users_client.get_all_users()

        assert e.value.response.status_code == 401


def test_search_users_not_found(users_client):
    users = users_client.get_all_users(search_query="nonexistent_user_12345")

    assert users == []


class TestUpdating:
    @pytest.mark.usefixtures("rollback_user")
    def test_update_user(self, users_client, user):
        user_for_edit = user
        new_fullname = "New Fullname"

        user_for_edit.fullname = new_fullname
        updated = users_client.update_user(user_for_edit)

        assert updated.fullname == new_fullname

    @pytest.mark.usefixtures("rollback_user")
    def test_update_user_too_long_firstname(self, users_client, user):
        user.firstname = "A" * 31

        with pytest.raises(HTTPError) as e:
            users_client.update_user(user)

        assert e.value.response.status_code == 400
        assert "First name can`t be longer than 30 characters" in e.value.response.text
