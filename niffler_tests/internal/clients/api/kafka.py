import json
import time
from typing import Callable, Optional

from confluent_kafka import TopicPartition
from confluent_kafka.admin import AdminClient
from confluent_kafka.cimpl import NewTopic, Consumer, Producer

from internal import settings
from internal.utils.common import wait_until_timeout
import logging

class KafkaClient:

    def __init__(
            self,
            client_id: str = 'tester',
            group_id: str = 'tester',

    ):
        self.server = settings.config.kafka_address
        self.admin = AdminClient(
            {"bootstrap.servers": f"{self.server}:9092"}
        )
        self.producer = Producer(
            {"bootstrap.servers": f"{self.server}:9092"}
        )
        self.consumer = Consumer(
            {
                "bootstrap.servers": f"{self.server}:9092",
                "group.id": group_id,
                "client.id": client_id,
                "auto.offset.reset": "latest",
                "enable.auto.commit": False,
                "enable.ssl.certificate.verification": False
            }
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.producer.flush()

    def list_topics_names(self, attempts: int = 5):
        try:
            topics = self.admin.list_topics(timeout=attempts).topics
            return [topics.get(item).topic for item in topics]
        except RuntimeError:
            logging.error("no topics in kafka")

    @wait_until_timeout
    def consume_message(self, partitions, **kwargs):
        self.consumer.assign(partitions)
        try:
            message = self.consumer.poll(1.0)
            logging.debug(f'{message.value()}')
            return message.value()
        except AttributeError:
            pass

    def get_last_offset(self, topic: str = "", partition_id=0):
        partition = TopicPartition(topic, partition_id)
        try:
            low, high = self.consumer.get_watermark_offsets(partition, timeout=5)
            return high
        except Exception as err:
            logging.error("probably no such topic: %s: %s", topic, err)
            return 0

    def subscribe_listen_new_offsets(self, topic):
        logging.info("subscribe")
        self.consumer.subscribe([topic])
        p_ids = self.consumer.list_topics(topic).topics[topic].partitions.keys()
        partitions_offsets_event = {k: self.get_last_offset(topic, k) for k in p_ids}
        logging.info(f'{topic} offsets: {partitions_offsets_event}')
        topic_partitions = [TopicPartition(topic, k, v) for k, v in partitions_offsets_event.items()]
        return topic_partitions

    def consume_message_filtered(
            self,
            topic_partitions: list[TopicPartition],
            predicate: Callable[[dict], bool],
            timeout: float = 10.0,
            poll_interval: float = 1.0
    ) -> Optional[dict]:
        self.consumer.assign(topic_partitions)

        start = time.time()
        while time.time() - start < timeout:
            msg = self.consumer.poll(poll_interval)
            if msg is None:
                continue
            if msg.error():
                logging.warning(f"Consumer error: {msg.error()}")
                continue

            try:
                data = json.loads(msg.value().decode('utf-8'))
                if predicate(data):
                    return data
            except Exception as e:
                logging.debug(f"Skipping malformed message: {e}")
                continue

        logging.warning(f"No matching message found within {timeout}s")
        return None