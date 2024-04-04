import os
import ast
import json
import logging

from urllib.parse import urlparse, ParseResult

from models.config import Config
from models.automation_f350 import F350AutomationSettings

def required_env(key):
    """
    Gets the provided key from os and if the value
    is None, raises an Exception
    """
    value = os.getenv(key)
    if value is None:
        raise Exception(f'{key} is a required env variable')
    return value


config: Config = None

start_request_schema: dict = None

update_request_schema: dict = None

f200_automation_settings: F350AutomationSettings = None

feed_strings: dict = None

logger = logging.getLogger()

def initialize():
    global config, start_request_schema, update_request_schema, f200_automation_settings, feed_strings

    # setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )

    kafka_brokers = required_env('KAFKA_BROKERS')
    kafka_brokers = [k.strip() for k in kafka_brokers.split(',')]

    strings = ast.literal_eval(required_env('FEED_STRINGS'))
    feed_strings = {}
    for string in strings:
        feed_strings[string.get('name')] = string

    config = Config(
        controls_plc_url = required_env('CONTROLS_PLC_URL'),
        epo_polling_interval = int(os.getenv('EPO_POLLING_INTERVAL', 3)),
        kafka_brokers = kafka_brokers,
        events_kafka_topic = os.getenv('EVENTS_KAFKA_TOPIC', 'feed.automation.events'),
        state_kafka_topic= os.getenv('STATE_KAFKA_TOPIC', 'feed.automation.state'),
        kafka_max_block_ms = int(os.getenv('KAFKA_MAX_BLOCK_MS', 1000)),
        kafka_retries = int(os.getenv('KAFKA_RETRIES', 5)),
        http_port = int(os.getenv('HTTP_PORT', 80)),
        state_publish_interval = int(os.getenv('STATE_PUBLISH_INTERVAL', 1)),
        offspeed_startup_threshold = int(os.getenv('OFFSPEED_STARTUP_THRESHOLD', 20)),
        offspeed_polling_interval = int(os.getenv('OFFSPEED_POLLING_INTERVAL', 30)),
        client_monitor_polling_interval = int(os.getenv('CLIENT_MONITOR_POLLING_INTERVAL', 5)),
        client_monitor_bomb_threshold = int(os.getenv('CLIENT_MONITOR_BOMB_THRESHOLD', 60)),
    )

    # load the schemas and resolve the $ref to the absolute path
    # to deal with local file references
    base_uri = urlparse("file://localhost")
    new_abs_path = os.path.abspath(base_uri.path[1:]) + '/../schemas/'
    resolved_ref = ParseResult(
        scheme=base_uri.scheme,
        netloc=base_uri.netloc,
        path=new_abs_path,
        params="",
        query="",
        fragment=""
    ).geturl()

    with open('./schemas/startAutomationRequest.json') as f:
        start_request_schema = json.load(f)
        start_request_schema['$id'] = resolved_ref

    with open('./schemas/updateAutomationRequest.json') as f:
        update_request_schema = json.load(f)
        update_request_schema['$id'] = resolved_ref

    # load the f200 automation settings
    f200_automation_settings = F350AutomationSettings(
        timeout_main_phase_completed = int(required_env("TIMEOUT_MAIN_PHASE_COMPLETED")),
        control_loop_sleep_period_main_phase = float(required_env("CONTROL_LOOP_SLEEP_PERIOD_MAIN_PHASE")),
    )