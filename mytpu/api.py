import json
import re
import sys
from typing import List
import requests
import cattr

from mytpu.models import (
    Account,
    AccountContext,
    CustomerResponse,
    Service,
    User,
    CheckMultipleAcctsResponse,
    AccountSummary,
    UserDetailsResponse,
    UserDetailsResponse,
)

# from hyper.contrib import HTTP20Adapter


class MyTPU:
    def __init__(self, username: str, password: str):
        self.username: str = username
        self.password: str = password

        self.session: requests.Session = requests.Session()
        # Couldn't seem to get this to work, and it doesn't seem necessary
        # self.session.mount('https://myaccount.mytpu.org', HTTP20Adapter())

        """ Token used to access the customer-oauth endpoint """
        self._oauth_token: str = None
        """ Customer access token """
        self._access_token: str = None

        self._user: User = None
        self.accounts: List[Account] = None
        self.account_summaries: List[AccountSummary] = None
        self.account_context: AccountContext = None

        self._customer: CustomerResponse = None

    @property
    def oauth_token(self) -> str:
        """
        In order to access the customer-oauth endpoint, we need a "basic auth" credential
        embedded in TPU's minified javascript. This is how we get it.
        """
        if not self._oauth_token:
            # First, we scan the login page for the main javascript content
            resp = self.session.get("https://myaccount.mytpu.org/eportal/")
            assert resp.status_code == 200, resp.content
            match = re.search(
                r'<script type="text/javascript" src="(main\.\w+\.js)"></script>',
                resp.content.decode(),
            )
            assert (
                match is not None
            ), "Could not find main.????.js on eportal login page"
            groups = match.groups()
            assert len(groups) == 1, "Could not find main.????.js on eportal login page"
            main_js = groups[0]
            # Then we scan the minified js code for the auth header used to access the oauth2 login API
            resp = self.session.get(f"https://myaccount.mytpu.org/eportal/{main_js}")
            assert resp.status_code == 200, resp.content
            match = re.search(
                r'{"Content-Type":"application/x-www-form-urlencoded",Authorization:"Basic (.+?)"}',
                resp.content.decode(),
            )
            assert match is not None, f"Could not find oauth token in {main_js}"
            groups = match.groups()
            assert len(groups) == 1, f"Could not find oauth token in {main_js}"
            self._oauth_token = groups[0]
        return self._oauth_token

    @property
    def access_token(self):
        if not self._access_token:
            resp = self.session.post(
                "https://myaccount.mytpu.org/rest/oauth/token",
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Authorization": f"Basic {self.oauth_token}",
                    # These are http/2 headers that I don't quite know how to send (hyper.contrib.HTTP20Adapter causes build failures)
                    # ':authority:': 'myaccount.mytpu.org',
                    # ':method:': 'POST',
                    # ':path:': '/rest/oauth/token',
                    # ':scheme:': 'https',
                },
                data={
                    "grant_type": "password",
                    "username": self.username,
                    "password": self.password,
                },
            )
            assert resp.status_code == 200, resp.content
            content = json.loads(resp.content)

            assert content["token_type"] == "bearer"
            assert content["scope"] == "read write"

            self._access_token = content["access_token"]
            # self.expires_in = content["expires_in"]  # e.g. 3599
            # self.refresh_token = content["refresh_token"]
            # self.jti = content["jti"]  # e.g. lower case uuid

            self._user = User.from_dict(content["user"])
            assert self._user.customerId, "no customerId value found in login response"
        return self._access_token

    @property
    def user(self) -> User:
        if not self._user:
            # User info is actually obtained as part of the login process.
            # Trigger the access_token property method to load it.
            _ = self.access_token
        return self._user

    def post(self, path: str, data=None, json=None, **kwargs) -> requests.Response:
        print(f"post to /rest/{path}", file=sys.stderr)
        kwargs.setdefault(
            "headers",
            {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.access_token}",
            },
        )
        resp = self.session.post(
            f"https://myaccount.mytpu.org/rest/{path}",
            data=data,
            json=json,
            **kwargs,
        )
        assert resp.status_code == 200, resp.content
        return resp

    def get_all_accounts(self) -> List[AccountSummary]:
        resp = self.post(
            "account/checkmultipleaccts/",
            json={
                "customerId": self.user.customerId,
                "csrViewOnly": "N",
                "firstTimeLogin": "N",
            },
        )
        content = json.loads(resp.content)
        response = CheckMultipleAcctsResponse.from_dict(content)
        assert response.statusCode == "200"
        assert (
            len(response.accSummaryTypes) == 1
        ), "I don't have access to multiple accounts. Will need user examples to add support for it."
        self.accounts = response.account
        self.account_summaries = response.accSummaryTypes
        return self.account_summaries

    def customer(self) -> CustomerResponse:
        """
        This call returns account info with lat/lon needed for the usage query
        """
        if not self._customer:
            resp = self.post(
                "account/customer/",
                json={
                    "customerId": self.user.customerId,
                    "accountContext": None,
                    "csrViewOnly": "N",
                },
            )
            assert resp.status_code == 200, resp.content
            content = json.loads(resp.content)
            assert content['statusCode'] == "200"
            self._customer = CustomerResponse.from_dict(content)
        return self._customer

    def get_user(self) -> User:
        assert self.user.customerId, "call login() first"
        resp = self.session.post(
            "https://myaccount.mytpu.org/rest/user",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.access_token}",
            },
            json={"customerId": self.user.customerId},
        )
        assert resp.status_code == 200, resp.content
        content = json.loads(resp.content)
        response = UserDetailsResponse.from_dict(content)
        assert response.statusCode == "200"
        # The other values in this request seem to be blank, so let's just return the user info
        return response.user

    def usage(
        self,
        context: AccountContext,
        service: Service,
        from_date: str,
        to_date: str,
        hourly=False,
    ):
        path = "usage/month/day" if hourly else "usage/month"
        resp = self.post(
            path,
            json={
                "customerId": self.user.customerId,
                "fromDate": from_date,  # "2022-05-17 12:00",
                "toDate": to_date,  # "2022-08-17 11:59",
                "meterNumber": service.meterNumber,
                "serviceNumber": service.serviceNumber,
                "serviceId": service.serviceId,
                "serviceType": service.serviceType,
                "accountContext": context.unstructure(),
                "latitude": service.latitude,
                "longitude": service.longitude,
                "contractNum": service.serviceContract,
                "netContractNum": service.netContractNum,
            },
        )
        content = json.loads(resp.content)
        return content

