from urllib.parse import urljoin
from typing import List

from internal.clients.api.base import BaseService
from internal.data.models.user import User


class UsersHttpClient(BaseService):
    def __init__(self, base_url: str, token: str):
        super().__init__(base_url, token)

    def get_current_user(self) -> User:
        resp = self.session.get(urljoin(self.base_url, "/api/users/current"))
        self._raise_for_status(resp)
        return User(**resp.json())

    def update_user(self, user: User) -> User:
        resp = self.session.post(
            urljoin(self.base_url, "/api/users/update"),
            json=user.model_dump(mode="json", exclude_none=True),
        )

        self._raise_for_status(resp)
        return User(**resp.json())

    def get_all_users(self, search_query: str | None = None) -> List[User]:
        params = {"searchQuery": search_query} if search_query else {}
        resp = self.session.get(urljoin(self.base_url, "/api/users/all"), params=params)
        self._raise_for_status(resp)
        return [User(**u) for u in resp.json()]
