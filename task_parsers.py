from html.parser import HTMLParser


class DeprovisioningTaskListParser(HTMLParser):
    task_list: list

    count_mode = False
    count: int

    name_mode = False
    name: str

    instanceId: str
    instance: dict

    def __init__(self):
        super().__init__()
        self.task_list = []

    def handle_starttag(self, tag, attrs):
        if tag == "li":
            for attr in attrs:
                if attr[0] == "id":
                    self.instanceId = attr[1][25:]
                    self.instance = {"instanceId": self.instanceId}
                    # self.task_list[self.instanceId] = {}
        if tag == "p":
            self.name_mode = True
        if tag == "div" and ("class", "task-instance-count rounded-4") in attrs:
            self.count_mode = True

    def handle_endtag(self, tag):
        if tag == "li":
            self.task_list.append(self.instance)
            self.instance = {}

    def handle_data(self, data):
        if self.name_mode:
            self.instance["instanceName"] = data.lstrip()
            self.name_mode = False
        if self.count_mode:
            self.instance["taskCount"] = int(data.strip())
            self.count_mode = False


class DeprovisioningTaskParser(HTMLParser):
    user_list = list

    user_mode = False
    email_mode = False
    unassign_date: str
    user: dict

    def __init__(self):
        super().__init__()
        self.user_list = []

    def handle_starttag(self, tag, attrs):
        if tag == "li":
            self.user = {}
        if tag == "div" and ("class", "task-details") in attrs:
            self.user_mode = True
        if tag == "p" and self.user_mode:
            self.email_mode = True
        if tag == "span" and ("class", "easydate") in attrs:
            self.unassign_date = attrs[1][1]

    def handle_data(self, data):
        if self.email_mode:
            self.user["email"] = data
            self.email_mode = False
            self.user_mode = False

    def handle_endtag(self, tag):
        if tag == "li":
            self.user["unassignedDate"] = self.unassign_date
            self.user_list.append(self.user)
            self.user = {}
