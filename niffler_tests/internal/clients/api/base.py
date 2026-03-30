import requests


from urllib.parse import urlparse, parse_qs


from internal.utils import allure_attach


class BaseSession(requests.Session):
    def __init__(self, *args, **kwargs):
        super().__init__()

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
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.session = BaseSession()
        self.session.headers.update(
            {
                "Accept": "application/json",
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            }
        )
        # self.session.hooks["response"].append(self.attach_response)

    """
    Alternative:

    @settingsaticmethod
    def attach_response(response: Response, *args, **kwargs):
        attachment_name = response.request.method + " " + response.request.url
        allure.attach(
            dump_response(response),
            attachment_name,
            attachment_type=AttachmentType.TEXT,
        )
    """

    def _raise_for_status(self, response: requests.Response):
        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            if response.status_code == 400:
                e.add_note(response.text)
            raise
