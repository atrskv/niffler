import random
from datetime import datetime, timedelta, timezone
import allure
import json
from json import JSONDecodeError

import curlify
from allure_commons.types import AttachmentType
from requests import Response

import re
import inspect
from functools import wraps

from allure_commons import plugin_manager
from allure_commons.utils import uuid4, func_parameters


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
        method, url = args[1], args[2]

        from jinja2 import Environment, PackageLoader, select_autoescape

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
