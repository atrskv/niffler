import os
import xmlschema
from jinja2 import Environment, FileSystemLoader, select_autoescape

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

env = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR), autoescape=select_autoescape(["xml"])
)


def current_user_xml(username: str) -> str:
    template = env.get_template("xml/current_user.xml")
    return template.render({"username": username})


def send_invitation_xml(username: str, friend: str) -> str:
    template = env.get_template("xml/send_invitation.xml")
    return template.render({"username": username, "friend": friend})


def xsd_response(
    operation: str, operation_namespace: str = "niffler-userdata"
) -> xmlschema.XMLSchema11:
    envelope_template = env.get_template("xsd/envelope.xsd")
    rendered = envelope_template.render(
        {
            "operation_xsd": f"{operation}.xsd",
            "operation": operation,
            "operation_namespace": operation_namespace,
        }
    )

    xsd_dir = os.path.join(TEMPLATES_DIR, "xsd")
    temp_path = os.path.join(xsd_dir, "temp.xsd")

    with open(temp_path, "w", encoding="utf-8") as f:
        f.write(rendered)

    return xmlschema.XMLSchema11(temp_path)

