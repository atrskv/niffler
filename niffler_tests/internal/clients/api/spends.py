from typing import List
import uuid
from urllib.parse import urljoin


from internal.clients.api.base import BaseService
from internal.data.models.spend import CategoryAPI, SpendAPI, SpendAddAPI


class SpendsHttpClient(BaseService):
    def __init__(self, base_url: str, token: str):
        super().__init__(base_url, token)

    def get_categories(self, exclude_archived: bool = True) -> list[CategoryAPI]:
        response = self.session.get(
            urljoin(self.base_url, "/api/categories/all"),
            params={"excludeArchived": str(exclude_archived).lower()},
        )
        self._raise_for_status(response)
        return [CategoryAPI(**c) for c in response.json()]

    def add_category(self, name: str) -> CategoryAPI:
        payload = {
            "id": str(uuid.uuid4()),
            "name": name,
        }
        response = self.session.post(
            urljoin(self.base_url, "/api/categories/add"),
            json=payload,
        )
        self._raise_for_status(response)
        return CategoryAPI(**response.json())

    def add_spend(self, spend: SpendAddAPI, username: str) -> SpendAPI:
        request_body = {
            "spendDate": spend.spendDate,
            "category": {
                "name": spend.category,
                "username": username,
            },
            "currency": spend.currency,
            "amount": spend.amount,
            "description": spend.description,
            "username": username,
        }

        response = self.session.post(
            urljoin(self.base_url, "/api/spends/add"),
            json=request_body,
        )

        self._raise_for_status(response)
        return SpendAPI(**response.json())

    def get_spends(
        self,
        filter_period: str | None = None,
        filter_currency: str | None = None,
    ) -> list[SpendAPI]:
        params = {}
        if filter_period:
            params["filterPeriod"] = filter_period
        if filter_currency:
            params["filterCurrency"] = filter_currency

        response = self.session.get(
            urljoin(self.base_url, "/api/spends/all"),
            params=params,
        )
        self._raise_for_status(response)
        return [SpendAPI(**s) for s in response.json()]

    def edit_spend(self, spend: SpendAPI) -> SpendAPI:
        resp = self.session.patch(
            urljoin(self.base_url, "/api/spends/edit"),
            json=spend.model_dump(mode="json", exclude_none=True),
        )
        self._raise_for_status(resp)
        return SpendAPI(**resp.json())

    def delete_spends(self, spend_ids: List[str]):
        params = {"ids": spend_ids}
        resp = self.session.delete(
            urljoin(self.base_url, "/api/spends/remove"), params=params
        )
        self._raise_for_status(resp)
