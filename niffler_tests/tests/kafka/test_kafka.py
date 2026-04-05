import json

from allure import step
import pytest

from internal.data.models.user import User, KafkaUserEvent


def test_message_should_be_produced_to_kafka_after_successful_registration(auth_client, kafka_client):
    user = User.random()

    topic_partitions = kafka_client.subscribe_listen_new_offsets("users")

    result = auth_client.register(user.username, user.password)
    assert result.status_code == 201

    def predicate(data):
        return data.get('username') == user.username

    event_data = kafka_client.consume_message_filtered(topic_partitions, predicate, timeout=10.0)

    assert event_data is not None, f"Сообщение для {user.username} не найдено"
    assert event_data['username'] == user.username


pytestmark = [
    pytest.mark.allure_label("KAFKA: Auth", label_type="epic"),
    pytest.mark.allure_label("Auth", label_type="feature"),
]

