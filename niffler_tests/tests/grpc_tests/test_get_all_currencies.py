from google.protobuf import empty_pb2
from internal.clients.pb.niffler_currency_pb2 import CurrencyValues
from internal.clients.pb.niffler_currency_pb2_pbreflect import (
    NifflerCurrencyServiceClient,
)
import pytest


pytestmark = [
    pytest.mark.allure_label("GRPC: Rates and currencies", label_type="epic"),
    pytest.mark.allure_label("Currencies", label_type="feature"),
]


def test_get_all_currencies(
    grpc_client: NifflerCurrencyServiceClient,
):
    expected = {
        CurrencyValues.RUB,
        CurrencyValues.USD,
        CurrencyValues.EUR,
        CurrencyValues.KZT,
    }

    response = grpc_client.get_all_currencies(empty_pb2.Empty())

    assert len(response.allCurrencies) == 4
    currencies = {c.currency: c.currencyRate for c in response.allCurrencies}
    assert set(currencies.keys()) == expected
    for rate in currencies.values():
        assert rate > 0, f"Currency rate {rate} should be positive"
