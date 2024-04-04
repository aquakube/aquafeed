import os
import json
import logging
import yaml
import jsonschema
from urllib.parse import urlparse, ParseResult

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

with open('../schemas/startAutomationRequest.json') as f:
    start_request_schema = json.load(f)
    start_request_schema['$id'] = resolved_ref

with open('../schemas/updateAutomationRequest.json') as f:
    update_request_schema = json.load(f)
    update_request_schema['$id'] = resolved_ref


def test_start_request_schema():
    for example in start_request_schema['examples']:
        jsonschema.validate(instance=example, schema=start_request_schema)


def test_update_request_schema():
    for example in update_request_schema['examples']:
        jsonschema.validate(instance=example, schema=update_request_schema)