import uuid
from datetime import datetime
from urllib.parse import urljoin

import requests


class SpendsHttpClient:
    session: requests.Session
    base_url: str

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

    def get_categories(self, exclude_archived=True):
        response = self.session.get(
            urljoin(
                self.base_url,
                "/api/categories/all",
            ),
            params={"excludeArchived": str(exclude_archived).lower()},
        )
        response.raise_for_status()

        return response.json()

    def add_category(self, name: str):
        response = self.session.post(
            urljoin(self.base_url, "/api/categories/add"),
            json={
                "id": str(uuid.uuid4()),
                "name": name,
            },
        )
        response.raise_for_status()

        return response.json()

    def add_spend(
        self,
        category_id: str,
        category_name: str,
        username: str,
        currency: str,
        amount: float,
        description: str,
        spend_date: datetime,
        archived: bool = False,
    ):
        request_body = {
            "spendDate": spend_date.isoformat(),
            "category": {
                "id": category_id,
                "name": category_name,
                "username": username,
                "archived": archived,
            },
            "currency": currency,
            "amount": amount,
            "description": description,
            "username": username,
        }

        endpoint_url = urljoin(self.base_url, "/api/spends/add")
        response = self.session.post(endpoint_url, json=request_body)
        response.raise_for_status()

        return response.json()

    def get_spends(
        self,
        filter_period: str | None = None,
        filter_currency: str | None = None,
    ):
        params = {}

        if filter_period is not None:
            params["filterPeriod"] = filter_period

        if filter_currency is not None:
            params["filterCurrency"] = filter_currency

        response = self.session.get(
            urljoin(self.base_url, "/api/spends/all"),
            params=params,
        )
        response.raise_for_status()

        return response.json()
