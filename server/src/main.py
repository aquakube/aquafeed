import time
import logging

import config

if __name__ == "__main__":
    
    config.initialize()

    from services.server import HttpServer
    from services.events import EventsConsumer
    from services.state import StateConsumer
    from services.epo import EPOThread
    from services.clients import ClientMonitorThread

    events_consumer = EventsConsumer()
    events_consumer.start()

    state_consumer = StateConsumer()
    state_consumer.start()

    server = HttpServer()
    server.start()

    epo = EPOThread()
    epo.start()

    client_monitor = ClientMonitorThread()
    client_monitor.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info('Got interrupt. Quitting.')
        events_consumer.stop()
        epo.stop()
        events_consumer.join()
        epo.join()