import requests


import allure
from allure_commons.types import AttachmentType
from requests import Response
from requests_toolbelt.utils.dump import dump_response


class BaseService:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.session = requests.session()
        self.session.headers.update(
            {
                "Accept": "application/json",
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            }
        )
        self.session.hooks["response"].append(self.attach_response)

    @staticmethod
    def attach_response(response: Response, *args, **kwargs):
        attachment_name = response.request.method + " " + response.request.url
        allure.attach(
            dump_response(response),
            attachment_name,
            attachment_type=AttachmentType.TEXT,
        )

    def _raise_for_status(self, response: requests.Response):
        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            if response.status_code == 400:
                e.add_note(response.text)
            raise
