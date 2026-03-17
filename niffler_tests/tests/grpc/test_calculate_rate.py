from internal.clients.pb.niffler_currency_pb2 import CalculateRequest, CurrencyValues
from internal.clients.pb.niffler_currency_pb2_pbreflect import (
    NifflerCurrencyServiceClient,
)
import grpc


def test_calculate_rate(grpc_client: NifflerCurrencyServiceClient) -> None:
    response = grpc_client.calculate_rate(
        request=CalculateRequest(
            spendCurrency=CurrencyValues.EUR,
            desiredCurrency=CurrencyValues.RUB,
            amount=100.0,
        )
    )

    assert response.calculatedAmount == 7200, "Expected 7200"


def test_calculate_rate__without_desired_currency(
    grpc_client: NifflerCurrencyServiceClient,
) -> None:
    try:
        _ = grpc_client.calculate_rate(
            request=CalculateRequest(
                spendCurrency=CurrencyValues.EUR,
                amount=100.0,
            )
        )
    except grpc.RpcError as e:
        assert e.code() == grpc.StatusCode.UNKNOWN
        assert e.details() == "Application error processing RPC"
