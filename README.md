# Proof of concept for Portal Registration Microservice

A simple proof-of-concept Flask app to serve as an intermediary between the PCDC portal and [the HubSpot's CRM API (v3)](https://developers.hubspot.com/docs/api/crm/understanding-the-crm), for the portal's user self-registration feature.

## Project setup

1. Download and install Python(^3.6)
2. Run `python3 -m venv env` to set up virtual environment
3. Run `source env/bin/activate` to activate virtual environment
4. Run `pip install -r requirements.txt` to install dependencies
5. Run `export FLASK_APP=app.py HUBSPOT_API_KEY=<your-api-key>`
6. Run `flask run`
7. Service is now running on port 5000

## Dependendcies

- `flask` for creating simple API server application
- `requests` for making HTTP calls

## Endpoints

### `POST /is-user-registered`

To check if the user with the given email already exists in the HubSpot contact list.

Expects the following payload:

```json
{
  "email": "jane.doe@uchicago.edu"
}
```

Returns something like:

```json
{
  "registered": false
}
```

### `POST /subscribe-user`

To create a new HubSpot contact using the provided information as properties.

Expects the following payload:

```json
{
  "email": "jane.doe@uchicago.edu",
  "firstname": "Jane",
  "institution": "The University of Chicago",
  "lastname": "Doe"
}
```

Returns something like:

```json
{
  "success": true
}
```

### `POST /get-user`

To get an existing user's information from HubSpot contacts.

Expects the following payload:

```json
{
  "email": "jane.doe@uchicago.edu"
}
```

Returns something like:

```json
{
  "firstname": "Jane",
  "institution": "The University of Chicago",
  "lastname": "Doe"
}
```

### `POST /update-user`

To update an existing user's information on HubSpot contacts.

`email` value is not modifiable and is only used to find the user. Updtabale proeprties include `firstname`, `lastname`, and `institution`. Information is not updated if the value is `null` or missing in the payload.

Expects the following payload:

```json
{
  "email": "jane.doe@uchicago.edu",
  "firstname": "Jane",
  "institution": "The University of Chicago Medical Center",
  "lastname": "Doe"
}
```

Returns something like:

```json
{
  "success": true
}
```
