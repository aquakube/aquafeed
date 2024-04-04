import json
from dataclasses import asdict

from flask import Blueprint, Response, jsonify, request
from kafka import KafkaConsumer, TopicPartition

import clients.state as state

from config import config
from utility import state as state_utility


mod = Blueprint('automation_state', __name__)

def create_kafka_consumer():
    consumer = KafkaConsumer(
        bootstrap_servers=config.kafka_brokers,
        auto_offset_reset='latest',
    )

    partition = TopicPartition(config.state_kafka_topic, 0)  # assuming one partition
    consumer.assign([partition])

    # get the latest offset for the assigned partition
    end_offsets = consumer.end_offsets([partition])
    start_offsets = consumer.beginning_offsets([partition])

    # set the starting offset to the latest offset
    starting_offset = end_offsets[partition]

    # reset the consumer to the starting offset
    consumer.seek(partition, starting_offset)

    return consumer, partition


@mod.route("/api/automation/state")
def stream():
    if 'Accept' in request.headers and request.headers['Accept'] == 'text/event-stream':
        return stream_state()

    else:
        return fetch_state()


def stream_state():

    def _state():
        consumer, partition = create_kafka_consumer()
        try:
            initial_message_sent = False
            state.increment_number_of_connected_clients()
            while True:
                if not initial_message_sent:
                    yield f"data: {json.dumps(state_utility.get_cloudevent(state.automation))}\n\n"
                    initial_message_sent = True
                messages = consumer.poll(timeout_ms=1000)
                if partition in messages:
                    for message in messages[partition]:
                        yield f"data: {message.value.decode('utf-8')}\n\n"
                else:
                    yield 'data: hearbeat\n\n'
        except:
            pass
        finally:
            state.decrement_number_of_connected_clients()
            consumer.close()

    return Response(_state(), mimetype='text/event-stream')


def fetch_state():
    automation = state.automation

    if automation is None:
        return jsonify({})

    return jsonify(asdict(automation))
