from typing import List
import requests
import xmlschema

from internal.clients.api.base import BaseService
from internal.soap.templates_reader import (
    current_user_xml,
    send_invitation_xml,
    xsd_response,
)


from internal.data.models.user import User


class UsersService(BaseService):
    def __init__(self, base_url: str, token: str = None):
        super().__init__(base_url, token)

    def get_current_user(self) -> User:
        resp = self.get("/api/users/current")
        self._raise_for_status(resp)
        return User(**resp.json())

    def update_user(self, user: User) -> User:
        resp = self.post(
            "/api/users/update",
            json=user.model_dump(mode="json", exclude_none=True),
        )

        self._raise_for_status(resp)
        return User(**resp.json())

    def get_all_users(self, search_query: str | None = None) -> List[User]:
        params = {"searchQuery": search_query} if search_query else {}
        resp = self.get("/api/users/all", params=params)
        self._raise_for_status(resp)
        return [User(**u) for u in resp.json()]


class UsersSoapService(BaseService):
    def __init__(self, base_url: str, token: str = None):
        super().__init__(base_url, token)
        self.session.headers.update({"Content-Type": "text/xml; charset=utf-8"})

    def _validate_response(self, response_text: str, schema_name: str) -> None:
        schema = xsd_response(schema_name)
        try:
            schema.validate(response_text)
        except xmlschema.validators.exceptions.XMLSchemaValidationError as e:
            raise AssertionError(
                f"SOAP ответ не соответствует схеме {schema_name}: {e}"
            )

    def get_current_user(self, username: str) -> requests.Response:
        xml_body = current_user_xml(username)
        resp = self.post("/ws", data=xml_body)
        self._raise_for_status(resp)
        self._validate_response(resp.text, "userResponse")
        return resp

    def send_invitation(self, user, friend) -> requests.Response:
        xml_body = send_invitation_xml(user, friend)
        resp = self.post("/ws", data=xml_body)
        self._raise_for_status(resp)
        self._validate_response(resp.text, "userResponse")
        return resp
