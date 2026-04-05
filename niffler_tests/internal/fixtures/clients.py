import pytest
from grpc import insecure_channel, intercept_channel

from internal import settings
from internal.clients.api.auth import AuthClient
from internal.clients.api.kafka import KafkaClient
from internal.clients.api.spends import SpendsService
from internal.clients.api.users import UsersService, UsersSoapService
from internal.clients.db.spends import SpendDb
from internal.clients.pb.niffler_currency_pb2_pbreflect import (
    NifflerCurrencyServiceClient,
)
from tests.conftest import INTERCEPTORS


@pytest.fixture
def spends_client(token) -> SpendsService:
    return SpendsService(
        f"{settings.config.gateway_url}:{settings.config.gateway_port}", token
    )


@pytest.fixture
def users_client(token) -> UsersService:
    return UsersService(
        f"{settings.config.gateway_url}:{settings.config.gateway_port}", token
    )


@pytest.fixture
def auth_client() -> AuthClient:
    return AuthClient(config=settings.config)


@pytest.fixture
def soap_users_client():
    return UsersSoapService(settings.config.soap_url)


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


@pytest.fixture(scope="session")
def kafka_client():
    with KafkaClient() as k:
        yield k
