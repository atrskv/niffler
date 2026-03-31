import pytest
from grpc import insecure_channel, intercept_channel

from internal import settings
from internal.clients.api.base import BaseService
from internal.clients.api.spends import SpendsHttpClient
from internal.clients.api.users import UsersHttpClient
from internal.clients.db.spends import SpendDb
from internal.clients.pb.niffler_currency_pb2_pbreflect import (
    NifflerCurrencyServiceClient,
)


@pytest.fixture
def spends_client(token) -> SpendsHttpClient:
    return SpendsHttpClient(
        f"{settings.config.gateway_url}:{settings.config.gateway_port}", token
    )


@pytest.fixture
def users_client(token) -> UsersHttpClient:
    return UsersHttpClient(
        f"{settings.config.gateway_url}:{settings.config.gateway_port}", token
    )


@pytest.fixture
def soap_users_client(token):
    service = BaseService(settings.config.soap_url)
    service.session.headers.update({"Content-Type": "text/xml; charset=utf-8"})
    return service


@pytest.fixture(scope="session")
def spend_db() -> SpendDb:
    return SpendDb(settings.config.spend_db_url)


@pytest.fixture(scope="session")
def grpc_client() -> NifflerCurrencyServiceClient:
    host = settings.config.currency_service_host

    if settings.config.use_mock:
        host = settings.config.wiremock_host

    channel = insecure_channel(host)
    intercepted_channel = intercept_channel(channel, *INTERCEPTORS)

    return NifflerCurrencyServiceClient(intercepted_channel)
