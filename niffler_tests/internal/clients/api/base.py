import requests


from urllib.parse import urlparse, parse_qs

from requests import Session

from internal.utils.allure import allure_attach


class TestSession(Session):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.code = None

    @allure_attach
    def request(self, method, url, **kwargs):
        response = super().request(method, url, **kwargs)
        for r in response.history:
            cookies = r.cookies.get_dict()
            self.cookies.update(cookies)
            code = parse_qs(urlparse(r.headers.get("Location")).query).get("code", None)
            if code:
                self.code = code
        return response


class BaseService:
    def __init__(self, base_url: str, token: str = None):
        self.base_url = base_url
        self.session = TestSession()
        self.session.headers.update(
            {
                "Accept": "application/json",
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            }
        )

    def _raise_for_status(self, response: requests.Response):
        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            if response.status_code == 400:
                e.add_note(response.text)
            raise

