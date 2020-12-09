import flask
from json import dumps
import os
import re
import requests

app = flask.Flask(__name__)  # default port 5000


def request_hubspot(data={}, method="POST", path="/"):
    url = "https://api.hubapi.com/crm/v3/objects" + path
    headers = {
        "accept": "application/json",
        "content-type": "application/json"
    }
    querystring = {"hapikey": os.getenv("HUBSPOT_API_KEY")}
    return requests.request(method, url, data=dumps(data), headers=headers, params=querystring)


def is_domain(name):
    # copied from https://validators.readthedocs.io/en/latest/_modules/validators/domain.html
    pattern = re.compile(
        r'^(([a-zA-Z]{1})|([a-zA-Z]{1}[a-zA-Z]{1})|'
        r'([a-zA-Z]{1}[0-9]{1})|([0-9]{1}[a-zA-Z]{1})|'
        r'([a-zA-Z0-9][-_.a-zA-Z0-9]{0,61}[a-zA-Z0-9]))\.'
        r'([a-zA-Z]{2,13}|[a-zA-Z0-9-]{2,30}.[a-zA-Z]{2,3})$'
    )
    return pattern.match(name)


@app.route("/is-user-registered", methods=["POST"])
def handle_find_user():
    args = flask.request.get_json()
    data = {
        "filterGroups": [{
            "filters": [{
                "value": args.get("email"),
                "propertyName": "email",
                "operator": "EQ"
            }]
        }],
        "properties": [""]
    }
    r = request_hubspot(data=data, path="/contacts/search")
    registered = r.json().get("total", 0) > 0
    return flask.jsonify({"registered": registered})


@app.route("/subscribe-user", methods=["POST"])
def subscribe_user():
    args = flask.request.get_json()
    data = {
        "properties": {
            "email": args.get("email"),
            "firstname": args.get("firstname"),
            "institution": args.get("institution"),
            "lastname": args.get("lastname"),
        }
    }
    r = request_hubspot(data=data, path="/contacts")
    success = r.status_code == requests.codes.created
    return flask.jsonify({"success": success})


@app.route("/get-user", methods=["POST"])
def get_user():
    args = flask.request.get_json()
    data = {
        "filterGroups": [{
            "filters": [{
                "value": args.get("email"),
                "propertyName": "email",
                "operator": "EQ"
            }]
        }],
        "properties": ["firstname", "lastname", "institution"]
    }
    r = request_hubspot(data=data, path="/contacts/search")
    user_properties = r.json().get("results")[0].get("properties")
    return flask.jsonify({"user": {
        "firstname": user_properties.get("firstname"),
        "lastname": user_properties.get("lastname"),
        "institution": user_properties.get("institution"),
    }})
