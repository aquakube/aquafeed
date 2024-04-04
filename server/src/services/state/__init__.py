import threading
import json
import logging
from collections import deque

from config import config
import clients.state as state

from kafka import KafkaProducer


class StateConsumer(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True, name="state_consumer")
        self.producer = KafkaProducer(
            bootstrap_servers=config.kafka_brokers,
            max_block_ms=config.kafka_max_block_ms,
            retries=config.kafka_retries,
            acks="all",
        )
        self.stop_event = threading.Event()

    def stop(self):
        self.stop_event.set()

    def run(self):
        state.publish(state=state.automation)
        while not self.stop_event.is_set():
            try:
                cloudevent = state.listen()
                if cloudevent is not None:
                    cloudevent = bytes(json.dumps(cloudevent), "utf-8")
                    future = self.producer.send(config.state_kafka_topic, cloudevent)
                    future.get()
            except:
                logging.exception("failed to publish state cloudevent to kafka")
