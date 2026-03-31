import pytest
import xmltodict


def test_current_user(soap_users_client, as_a_registered_user):
    user = as_a_registered_user

    response = soap_users_client.get_current_user(user.username)

    data = xmltodict.parse(response.text)
    user_data = data["SOAP-ENV:Envelope"]["SOAP-ENV:Body"]["ns2:userResponse"][
        "ns2:user"
    ]
    assert user_data["ns2:username"] == user.username


def test_send_invitation(soap_users_client, as_a_registered_user, friend):
    user_1 = as_a_registered_user
    user_2 = friend

    response = soap_users_client.send_invitation(user_1.username, user_2.username)

    assert response.status_code == 200
    data = xmltodict.parse(response.text)
    user_data = data["SOAP-ENV:Envelope"]["SOAP-ENV:Body"]["ns2:userResponse"][
        "ns2:user"
    ]
    assert user_data["ns2:username"] == user_2.username
    assert user_data["ns2:friendshipStatus"] == "INVITE_SENT"


pytestmark = [
    pytest.mark.allure_label("SOAP: Users", label_type="epic"),
]
