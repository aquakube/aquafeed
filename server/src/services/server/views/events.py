from flask import Blueprint, Response, copy_current_request_context
from kafka import KafkaConsumer, TopicPartition

from config import config

mod = Blueprint('automation_events', __name__)

def create_kafka_consumer():
    consumer = KafkaConsumer(
        bootstrap_servers=config.kafka_brokers,
        auto_offset_reset='latest',
    )

    partition = TopicPartition(config.events_kafka_topic, 0)  # assuming one partition
    consumer.assign([partition])

    # get the latest offset for the assigned partition
    end_offsets = consumer.end_offsets([partition])
    start_offsets = consumer.beginning_offsets([partition])

    # set the starting offset to the latest offset minus 100
    # or the beginning offset, whichever is greater
    starting_offset = max(start_offsets[partition], end_offsets[partition] - 100)

    # reset the consumer to the starting offset
    consumer.seek(partition, starting_offset)

    return consumer, partition


@mod.route("/api/automation/events")
def stream():

    def _events():
        consumer, partition = create_kafka_consumer()
        try:
            while True:
                messages = consumer.poll(timeout_ms=1000)
                if partition in messages:
                    for message in messages[partition]:
                        yield f"data: {message.value.decode('utf-8')}\n\n"
                else:
                    yield 'data: hearbeat\n\n'
        except:
            pass
        finally:
            consumer.close()

    return Response(_events(), mimetype='text/event-stream')