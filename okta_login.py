"""Call Okta APIs using Session (cookies) and xsrfToken -- just like a browser. SSWS API Token is not needed.

### CAUTION: Code to call private APIs is not supported by Okta. The APIs can change at any time.
###          Test in a dev or oktapreview tenant before trying this in production.

This will work with users who have Push MFA. This won't work if Security > General > "MFA for Admins" is enabled.
"""

import requests
import time
import re
from os import environ

import config

# Change the following lines.
# okta_url = environ.get("OKTA_URL")
# okta_admin_url = environ.get("OKTA_ADMIN_URL")


def admin_login(username, password, okta_url, okta_admin_url, session):
    sign_in(username, password, okta_url, session)
    user = get_user(okta_url, session)
    admin_xsrf_token = admin_sign_in(okta_url, okta_admin_url, session)
    return session
    # send_notification(admin_xsrf_token, user["id"])
    # get_user_factors(user["id"])


def sign_in(username, password, okta_url, session):
    print("URL:", okta_url)
    print("Username:", username)
    print("Signing in...")
    response = session.post(
        okta_url + "/api/v1/authn", json={"username": username, "password": password}
    )
    authn = response.json()
    if not response.ok:
        print(authn["errorSummary"])
        exit()

    if authn["status"] == "MFA_REQUIRED":
        token = send_push(authn["_embedded"]["factors"], authn["stateToken"])
    else:
        token = authn["sessionToken"]

    session.get(okta_url + "/login/sessionCookieRedirect?redirectUrl=/&token=" + token)


def send_push(factors, state_token):
    print("Push MFA...")
    push_factors = [f for f in factors if f["factorType"] == "push"]
    if len(push_factors) == 0:
        print("Push factor not found")
        exit()
    push_url = push_factors[0]["_links"]["verify"]["href"]
    while True:
        authn = session.post(push_url, json={"stateToken": state_token}).json()
        if authn["status"] == "SUCCESS":
            return authn["sessionToken"]
        result = authn["factorResult"]
        if result == "WAITING":
            time.sleep(4)
            print("Waiting...")
        elif result in ["REJECTED", "TIMEOUT"]:
            print("Push rejected")
            exit()


def admin_sign_in(okta_url, okta_admin_url, session):
    response = session.get(okta_url + "/home/admin-entry")
    match = re.search(r'"token":\["(.*)"\]', response.text)
    if not match:
        print(
            "admin_sign_in: token not found. Go to Security > General and disable Multifactor for Administrators."
        )
        exit()
    body = {"token": match.group(1)}

    response = session.post(okta_admin_url + "/admin/sso/request", data=body)
    match = re.search(r'<span.* id="_xsrfToken">(.*)</span>', response.text)
    admin_xsrf_token = match.group(1)
    return admin_xsrf_token


def get_user(okta_url, session):
    user = session.get(okta_url + "/api/v1/users/me").json()
    return user


def get_user_factors(userid):
    factors = session.get(okta_url + "/api/v1/users/" + userid + "/factors").json()
    print(factors)

