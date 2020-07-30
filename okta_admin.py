import requests
import json
from html.parser import HTMLParser

from okta_login import admin_login

from task_parsers import *


class OktaAdminSession(requests.Session):
    """Requests Session that is logged into Okta Admin
    and capable of interacting with the Okta Admin Private API."""

    base_url: str
    admi_url: str

    def __init__(self, username, password, subdomain, preview=False):
        super().__init__()
        if preview:
            environment = "preview"
        else:
            environment = ""
        self.base_url = "https://{}.okta{}.com".format(subdomain, environment)
        self.admin_url = "https://{}-admin.okta{}.com".format(subdomain, environment)
        admin_login(username, password, self.base_url, self.admin_url, self)

    def strip_js(self, text):
        # Strip leftover JS text from response
        json_data = json.loads(text[11:])
        return json_data

    def get_app_instance_name(self, instanceId):
        # Get the app instance name
        url = "{}/api/v1/apps/{}".format(self.base_url, instanceId)
        app_profile = self.get(url).json()
        instance_name = app_profile["name"]
        return instance_name

    def get_app_instance_features(self, instanceId):
        # Retrieve an app instance's enabled features from the tags API
        def tags_to_dict(tag_json):
            # Map to dict
            tag_dict = {}
            for item in tag_json:
                tag_dict[item["image"]] = {
                    "displayName": item["displayName"],
                    "active": item["active"],
                }
            return tag_dict

        instanceName = self.get_app_instance_name(instanceId)
        url = "{}/admin/app/{}/instance/{}/tags".format(
            self.admin_url, instanceName, instanceId
        )
        tags_json = self.strip_js(self.get(url).text)
        tags = tags_to_dict(tags_json["tags"])
        app_data = {
            "appInstanceName": instanceName,
            "appInstanceId": instanceId,
            "features": tags,
        }
        return app_data

    def get_tasks(
        self,
        taskType="main",
        taskDate="ALL",
        selectedUserId=None,
        selectedGroupId=None,
        selectedAppId=None,
        instanceId=None,
        firstResult=None,
    ):

        url = "{}/admin/tasks/{}".format(self.admin_url, taskType)
        params = {
            "taskDate": taskDate,
            "selectedUserId": selectedUserId,
            "selectedGroupId": selectedGroupId,
            "selectedAppId": selectedAppId,
            "instanceId": instanceId,
            "firstResult": firstResult,
        }
        {k: v for k, v in params.items() if v is not None}

        def deprovisioning_tasks():
            nonlocal url, params
            if instanceId is not None:
                url = "{}/instance".format(url)
                params["firstResult"] = 0
                tasks = self.get(url, params=params).text
                parser = DeprovisioningTaskParser()
                parser.feed(tasks)
                result = parser.user_list
            else:
                tasks = self.get(url, params=params).text
                parser = DeprovisioningTaskListParser()
                parser.feed(tasks)
                task_list = parser.task_list
                for index, item in enumerate(task_list):
                    parser = DeprovisioningTaskParser()
                    instanceTasks = self.get_tasks(
                        taskType="deprovisioning", instanceId=item["instanceId"]
                    )
                    task_list[index]["tasks"] = instanceTasks
                result = task_list
            return result

        if taskType == "main":
            tasks = self.get(url, params=params).text
            tasks = self.strip_js(tasks)
            del tasks["pendo"], tasks["timeLimitedOrg"]
        elif taskType == "deprovisioning":
            tasks = deprovisioning_tasks()
        return tasks
