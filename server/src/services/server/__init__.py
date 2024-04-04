import logging
import threading

from flask import Flask
from flask_cors import CORS

import clients.events as events
import clients.state as state
from config import config

app = Flask(__name__)
cors = CORS(app,
    resources={r"/*": {"origins": "*"}},
    supports_credentials=True
)

from .views import start_automation
from .views import stop_automation
from .views import pause_automation
from .views import resume_automation
from .views import update_automation
from .views import reset_automation
from .views import events
from .views import state
from .views import epo
from .views import feed_string

app.register_blueprint(start_automation.mod)
app.register_blueprint(stop_automation.mod)
app.register_blueprint(pause_automation.mod)
app.register_blueprint(resume_automation.mod)
app.register_blueprint(update_automation.mod)
app.register_blueprint(reset_automation.mod)
app.register_blueprint(events.mod)
app.register_blueprint(state.mod)
app.register_blueprint(epo.mod)
app.register_blueprint(feed_string.mod)

@app.route('/')
@app.route('/specs')
@app.route('/advanced')
def index():
    return app.send_static_file('index.html')

class HttpServer(threading.Thread):
    """
    Creates a new flask HTTP server.
    """

    def __init__(self):
        super().__init__(name='http_server', daemon=True)


    def run(self):
        # if debug is set to True, you can't access
        # flask across a network
        app.debug = False

        try:
            app.run(
                host='0.0.0.0',
                port=config.http_port,
                threaded=True,
                debug=False
            )
        except KeyboardInterrupt:
            logging.info('Flask got interrupt. Quitting.')