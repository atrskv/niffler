import base64
import hashlib
import os
import re

import requests

from internal.clients.api.base import TestSession
from internal.settings import Config


class AuthClient:
    def __init__(self, config: Config):
        self.session = TestSession()
        self.domain_url = f"{config.auth_url}:{config.auth_port}"
        self.code_verifier = base64.urlsafe_b64encode(os.urandom(32)).decode("utf-8")
        self.code_verifier = re.sub("[^a-zA-Z0-9]+", "", self.code_verifier)

        self.code_challenge = hashlib.sha256(
            self.code_verifier.encode("utf-8")
        ).digest()
        self.code_challenge = base64.urlsafe_b64encode(self.code_challenge).decode(
            "utf-8"
        )
        self.code_challenge = self.code_challenge.replace("=", "")

        self._basic_token = base64.b64encode(config.auth_secret.encode("utf-8")).decode(
            "utf-8"
        )
        self.authorization_basic = {"Authorization": f"Basic {self._basic_token}"}
        self.token = None

    def auth(self, username, password):
        self.session.get(
            url=f"{self.domain_url}/oauth2/authorize",
            params={
                "response_type": "code",
                "client_id": "client",
                "scope": "openid",
                "redirect_uri": "http://frontend.niffler.dc/authorized",
                "code_challenge": self.code_challenge,
                "code_challenge_method": "S256",
            },
            allow_redirects=True,
        )

        self.session.post(
            url=f"{self.domain_url}/login",
            data={
                "username": username,
                "password": password,
                "_csrf": self.session.cookies.get("XSRF-TOKEN"),
            },
            allow_redirects=True,
        )

        token_response = self.session.post(
            url=f"{self.domain_url}/oauth2/token",
            data={
                "code": self.session.code,
                "redirect_uri": "http://frontend.niffler.dc/authorized",
                "code_verifier": self.code_verifier,
                "grant_type": "authorization_code",
                "client_id": "client",
            },
        )

        self.token = token_response.json().get("access_token", None)
        return self.token
