from os import environ

from flask import Flask, jsonify, request, url_for

from okta_admin import OktaAdminSession
import config

app = Flask(__name__)
USERNAME = environ.get("OKTA_ADMIN_USERNAME")
PASSWORD = environ.get("OKTA_ADMIN_PASSWORD")
OKTA_SUBDOMAIN = environ.get("OKTA_SUBDOMAIN")
OKTA_ENVIRONMENT = environ.get("OKTA_ENVIRONMENT")


def create_session():
    if OKTA_ENVIRONMENT == "PREVIEW":
        preview = True
    else:
        preview = False
    session = OktaAdminSession(USERNAME, PASSWORD, OKTA_SUBDOMAIN, preview=preview)
    return session


@app.route("/instance/<instanceId>", methods=["GET"])
def get_instance_info(instanceId):
    session = create_session()
    results = session.get_app_instance_features(instanceId)
    return jsonify(results)


@app.route("/tasks", methods=["GET"])
def all_tasks():
    session = create_session()
    results = session.get_tasks()
    return jsonify(results)


@app.route("/tasks/deprovisioning", methods=["GET"])
def deprovisioning_tasks():
    args = request.args
    session = create_session()
    if args.get("instanceId", default=None):
        results = session.get_tasks(
            taskType="deprovisioning", instanceId=args.get("instanceId")
        )
    else:
        results = session.get_tasks(taskType="deprovisioning")
    return jsonify(results)


@app.route("/tasks/deprovisioning/<instanceId>", methods=["GET"])
def instance_deprovisioning_tasks(instanceId):
    session = create_session()
    results = session.get_tasks(taskType="deprovisioning", instanceId=instanceId)
    return jsonify(results)


if __name__ == "__main__":
    app.run(host="127.0.0.1")

