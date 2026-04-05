from typing import Literal
import dotenv
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    context: Literal["local", "remote"] = "remote"
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
    spend_db_url: str | None = None
    auth_secret: str | None = None
    test_username: str | None = None
    test_password: str | None = None
    test_fullname: str | None = None
    soap_url: str | None = None
    window_height: str | None = '1920'
    window_width: str | None = '1080'

    selenoid_url: str | None = None
    driver_name: str | None = None
    driver_version: str | None = None
    enable_video: bool | None = None
    enable_VNC: bool| None = None


config = Config(_env_file=dotenv.find_dotenv(f"config.{Config().context}.env"))
