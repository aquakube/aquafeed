import threading
import json
import logging
from collections import deque

from config import config
import clients.events as events

from kafka import KafkaProducer


class EventsConsumer(threading.Thread):


    def __init__(self):
        super().__init__(daemon=True, name='events_consumer')
        self.producer = KafkaProducer(
            bootstrap_servers=config.kafka_brokers,
            max_block_ms=config.kafka_max_block_ms,
            retries=config.kafka_retries,
            acks='all',
        )
        self.stop_event = threading.Event()


    def stop(self):
        self.stop_event.set()


    def run(self):
        while not self.stop_event.is_set():
            try:
                event = events.listen()
                if event is not None:

                    # publish event to kafka
                    cloudevent = bytes(json.dumps(event), 'utf-8')
                    future = self.producer.send(config.events_kafka_topic, cloudevent)
                    future.get()
            except:
                logging.exception('failed to publish event to kafka')