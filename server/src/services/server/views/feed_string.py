import os
import ast
import logging

from flask import Response, Blueprint, jsonify

from config import feed_strings


mod = Blueprint('feed_string', __name__)

@mod.route("/api/automation/feedstring", methods=['GET'])
def feed_string():
    """ Fetches the feed strings from the Servers configuration list """
    try:
        return jsonify(ast.literal_eval(os.getenv('FEED_STRINGS')))
    except:
        logging.exception('Failed to send feed string configurations!')
        return Response(status=500)
