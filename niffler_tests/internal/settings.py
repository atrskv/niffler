from typing import Literal
import dotenv
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    context: Literal["local", "remote"] = "local"
    use_mock: bool = False
    frontend_url: str = "http://frontend.niffler.dc"
    wiremock_host: str = "localhost:8094"
    currency_service_host: str = "localhost:8094"
    auth_url: str | None = None
    auth_port: str | None = None
    auth_domain: str | None = None
    gateway_url: str | None = None
    gateway_port: str | None = None
    timeout: float = 5.0


config = Config(_env_file=dotenv.find_dotenv(f"config.{Config().context}.env"))
