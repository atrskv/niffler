import pytest

from internal.data.models.user import User
from internal.utils.common import log_in_user, register_user


@pytest.fixture(scope="function")
def as_a_registered_user():
    user = User.random()
    register_user(user)
    return user


@pytest.fixture(scope="function")
def as_a_logged_user(as_a_registered_user, in_browser):
    _ = in_browser
    user = as_a_registered_user
    log_in_user(user)
    return user


@pytest.fixture(scope="function")
def friend():
    friend = User.random()
    register_user(friend)
    return friend
