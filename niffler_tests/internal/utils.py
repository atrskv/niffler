import inspect
import json
import random
import re
from datetime import datetime, timedelta, timezone
from functools import wraps
from json import JSONDecodeError

import allure
import curlify
import requests
from allure_commons import plugin_manager
from allure_commons.types import AttachmentType
from allure_commons.utils import func_parameters, uuid4
from jinja2 import Environment, PackageLoader, select_autoescape
from requests import Response

from internal import settings
from internal.data.models.user import User


def random_recent_days(days=30):
    now = datetime.now(timezone.utc)
    delta = timedelta(days=random.randint(0, days))
    return now - delta


def step(title, display_params=True):
    if callable(title):
        func = title
        name: str = title.__name__
        # todo: move to StepContext
        display_name = re.sub(r"_+", " ", name)
        return StepContext(display_name, {}, display_params=display_params)(func)
    else:
        return StepContext(title, {})


class StepContext:
    def __init__(self, title, params, display_params=True):
        self.title = title
        self.params = params
        self.uuid = uuid4()
        self.display_params = display_params

    def __enter__(self):
        plugin_manager.hook.start_step(
            uuid=self.uuid, title=self.title, params=self.params
        )

    def __exit__(self, exc_type, exc_val, exc_tb):
        plugin_manager.hook.stop_step(
            uuid=self.uuid,
            title=self.title,
            exc_type=exc_type,
            exc_val=exc_val,
            exc_tb=exc_tb,
        )

    def __call__(self, func):
        @wraps(func)
        def impl(*args, **kw):
            __tracebackhide__ = True

            params = func_parameters(func, *args, **kw)
            params_values = list(params.values())
            stringified_params = ", ".join(params_values)

            def params_to_display():
                if not params_values:
                    return ""
                if len(params_values) == 1:
                    return " " + params_values[0]
                return ": " + stringified_params

            def context():
                ismethod = lambda fn: (
                    args and inspect.getfullargspec(fn).args[0] in ["cls", "self"]
                )

                module_name = (
                    func.__module__.split(".")[-1] if not ismethod(func) else None
                )

                instance = args[0] if ismethod(func) else None
                instance_desc = str(instance)
                instance_name = instance_desc if "at 0x" not in instance_desc else None
                class_name = instance and instance.__class__.__name__

                context = module_name or instance_name or class_name

                if not context:
                    return ""

                return f" [{context}]"

            name_to_display = (
                self.title
                + (params_to_display() if self.display_params else "")
                + context()
            )

            with StepContext(name_to_display, params):
                return func(*args, **kw)

        return impl


def allure_attach(function):

    def wrapper(*args, **kwargs):
        method = kwargs.get("method") or (args[1] if len(args) > 1 else "UNKNOWN")

        url = kwargs.get("url")
        if url is None:
            self_obj = args[0] if args else None
            url = getattr(self_obj, "base_url", "UNKNOWN")

        env = Environment(
            loader=PackageLoader("internal", "allure_templates"),
            autoescape=select_autoescape(),
        )

        request_template = env.get_template("http-colored-request.ftl")
        response_template = env.get_template("http-colored-response.ftl")

        with allure.step(f"{method} {url}"):
            response: Response = function(*args, **kwargs)

            curl = curlify.to_curl(response.request)
            request_render = request_template.render(
                {
                    "request": response.request,
                    "curl": curl,
                }
            )

            allure.attach(
                body=request_render,
                name="Request",
                attachment_type=AttachmentType.HTML,
                extension=".html",
            )

            try:
                body = json.dumps(response.json(), indent=4, ensure_ascii=False)
            except (JSONDecodeError, TypeError):
                body = response.text

            response_render = response_template.render(
                {
                    "response": response,
                    "body": body,
                }
            )

            allure.attach(
                body=response_render,
                name=f"Response {response.status_code}",
                attachment_type=AttachmentType.HTML,
                extension=".html",
            )

        return response

    return wrapper


def register_user(user: User):
    session = requests.Session()

    session.get(
        f"{settings.config.auth_url}:{settings.config.auth_port}/register",
        verify=False,
    )
    csrf_token = session.cookies.get("XSRF-TOKEN")

    response = session.post(
        f"{settings.config.auth_url}:{settings.config.auth_port}/register",
        data={
            "username": user.username,
            "password": user.password,
            "passwordSubmit": user.password,
            "_csrf": csrf_token,
        },
        headers={"X-XSRF-TOKEN": csrf_token},
        verify=False,
    )

    if response.status_code != 201:
        raise Exception("Failed to register user")
