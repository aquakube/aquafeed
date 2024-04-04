from dataclasses import dataclass

@dataclass
class Config:

    controls_plc_url: str

    kafka_brokers: 'list[str]'

    events_kafka_topic: str

    state_kafka_topic: str

    kafka_max_block_ms: int

    kafka_retries: int

    http_port: int

    epo_polling_interval: int

    state_publish_interval: int

    offspeed_startup_threshold: int

    offspeed_polling_interval: int

    client_monitor_polling_interval: int

    client_monitor_bomb_threshold: int
