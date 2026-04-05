import json

from allure import step
import pytest

from internal.data.models.user import User, KafkaUserEvent


def test_message_should_be_produced_to_kafka_after_successful_registration(auth_client, kafka_client):
        user = User.random()
        topic_partitions = kafka_client.subscribe_listen_new_offsets("users")

        result = auth_client.register(user.username, user.password)
        assert result.status_code == 201

        event = kafka_client.consume_message(topic_partitions)

        with step("Check that message from kafka exist"):
            assert event != '' and event != b''

        with step("Check message content"):
            KafkaUserEvent.model_validate(json.loads(event.decode('utf8')))
            assert json.loads(event.decode('utf8'))['username'] == user.username


pytestmark = [
    pytest.mark.allure_label("KAFKA: Auth", label_type="epic"),
    pytest.mark.allure_label("Auth", label_type="feature"),
]

