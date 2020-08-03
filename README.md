# OktaPrivateAPI
###### Interface for communicating with the Okta Private API
**DISCLAIMERS:**
* The Okta Private API is undocumented and unsupported by Okta, it could change at any time. Use these tools at your own risk, and consider testing in Preview before using in Production
* These tools are still under active development. You may encounter unexpected, non-graceful errors.
* Enforcing MFA for Admin Portal login must be disabled for your org, and your service account admin must not be subject to MFA. Support for enabling this feature and requiring MFA for the admin account will be added in a future release.

---
## Overview

This project intends to help expose and interact with the data only available in the private Okta Admin API (the underlying API for certain actions within the Okta Admin UI).



It requires a username and password for an Okta Administrator service account in your org. 


Actions currently supported:
* Retrieiving enabled features for a given app instance ID, i.e. provisioning features like Import Users or Create Users
* Retrieving a count of all tasks from the Admin Tasks page
* Retrieving a list of all deprovisioning tasks for an Okta tenant
* Retrieving a list of deprovisioning tasks for a specific app instance

### Setup
1. `pip install requirements.txt`
2. Copy `.env_sample` to `.env` and add your environment info

### Usage
OktaPrivateAdmin can be used in one of two ways; As a backend for a Flask app (example included), or as an importable module. 

`okta_admin.py` provides `OktaAdminSession` which is a python-requests Session object. It supports all normal functions for a Session, plus some custom functions specific to the Private API. Below is example usage of importing `OktaAdminSession`. 
```python
from okta_admin import OktaAdminSession

USERNAME = "kingroland"
PASSWORD = "12345"
SUBDOMAIN = "druidia"
APP_INSTANCE_ID = "014235w3034534wx"

adminsession = OktaAdminSession(USERNAME, PASSWORD, SUBDOMAIN, preview=False)

enabled_features = adminsession.get_app_instance_features(APP_INSTANCE_ID)
print(enabled_features)
```


### Notes

Special thanks to [@Gabriel Sroka](https://github.com/gabrielsroka) on MacAdmins Slack who shared the code that `okta_login.py` is based off of.

The Private API will typically respond with either JSON* or HTML. A custom HTMLParser from `html.parser` is used to translate this into JSON. These parsers are found in `parsers.py`.

**When an endpoint responds with JSON, it will include some leftover JS as the first 11 characters. The custom methods for `OktaAdminSession` account for this with the `strip_js` class method. If making calls to currently unsupported endpoints, you may need to wrap your results with this method.* 