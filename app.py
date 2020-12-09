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


@app.route("/list-companies", methods=["GET"])
def list_companies():
    companies = []
    after = 0

    while True:
        data = {
            "limit": 100,
            "after": after,
            "filterGroups": [{
                "filters": [{
                    "propertyName": "name",
                    "operator": "HAS_PROPERTY"
                }]
            }]
        }
        r = request_hubspot(data=data, path="/companies/search")
        json = r.json()
        results = json.get("results", [])

        for result in results:
            company = result.get("properties", {}).get("name", None)
            if company is not None and not is_domain(company):
                companies.append(company)

        if json.get("paging", None) is not None:
            after = json.get("paging").get("next").get("after")
        else:
            break

    return flask.jsonify({"companies": sorted(set(companies))})


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
