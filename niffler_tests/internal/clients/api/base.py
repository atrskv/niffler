import requests
from urllib.parse import urljoin
from requests import Session
from internal.utils.allure import allure_attach


class BaseSession(Session):
    def __init__(self, base_url: str = None):
        super().__init__()
        self.base_url = base_url.rstrip("/") if base_url else None

    def request(self, method, url, **kwargs):
        if self.base_url and not url.startswith(("http://", "https://")):
            url = urljoin(self.base_url + "/", url)
        return super().request(method, url, **kwargs)


class BaseService:
    def __init__(self, base_url: str, token: str = None):
        self.session = BaseSession(base_url)

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        if token:
            headers["Authorization"] = f"Bearer {token}"

        self.session.headers.update(headers)

    @allure_attach
    def get(self, endpoint: str, **kwargs):
        return self.session.get(endpoint, **kwargs)

    @allure_attach
    def post(self, endpoint: str, **kwargs):
        return self.session.post(endpoint, **kwargs)

    @allure_attach
    def put(self, endpoint: str, **kwargs):
        return self.session.put(endpoint, **kwargs)

    @allure_attach
    def patch(self, endpoint: str, **kwargs):
        return self.session.patch(endpoint, **kwargs)

    @allure_attach
    def delete(self, endpoint: str, **kwargs):
        return self.session.delete(endpoint, **kwargs)

    def _raise_for_status(self, response: requests.Response):
        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            if response.status_code == 400:
                e.add_note(response.text)
            raise

