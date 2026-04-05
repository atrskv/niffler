import inspect
import json
import re
from functools import wraps
from json import JSONDecodeError

import allure
import curlify

from allure_commons import plugin_manager
from allure_commons.types import AttachmentType
from allure_commons.utils import uuid4, func_parameters
from jinja2 import Environment, PackageLoader, select_autoescape
from requests import Response
from selene import browser

from internal import settings


def step(title, display_params=True):
    if callable(title):
        func = title
        name: str = title.__name__
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
        self_obj = args[0] if args else None

        method = kwargs.get("method") or (function.__name__.upper())

        endpoint = args[1] if len(args) > 1 else ""
        base_url = getattr(self_obj, "base_url", "")

        url = kwargs.get("url") or f"{base_url}{endpoint}"

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


def add_screenshot():
    png = browser.driver.get_screenshot_as_png()
    allure.attach(
        body=png,
        name='Screenshot',
        attachment_type=AttachmentType.PNG,
        extension='.png',
    )


def add_browser_logs():
    log = ''.join(
        f'{text}\n' for text in browser.driver.get_log(log_type='browser')
    )
    allure.attach(log, 'Browser logs', AttachmentType.TEXT, '.log')


def add_html():
    html = browser.driver.page_source
    allure.attach(html, 'Page source', AttachmentType.HTML, '.html')


def add_video():
    video_url = (
        f'https://{settings.config.selenoid_url}/video/'
        + browser.driver.session_id
        + ".mp4"
    )
    html = (
        '<html><body><video width=\'100%\' height=\'100%\' controls autoplay><source src='
        + video_url
        + ' type=\'video/mp4\'></video></body></html>'
    )
    allure.attach(
        html,
        'Video. Session id: ' + browser.driver.session_id,
        AttachmentType.HTML,
        '.html',
    )
