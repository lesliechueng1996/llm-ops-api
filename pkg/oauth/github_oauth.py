"""
@Time   : 2024/12/28 17:29
@Author : Leslie
@File   : github_oauth.py
"""

from pkg.oauth.oauth import OAuth, OAuthUserInfo
import urllib
import requests


class GithubOAuth(OAuth):
    _AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
    _ACCESS_TOKEN_URL = "https://github.com/login/oauth/access_token"
    _USER_INFO_URL = "https://api.github.com/user"
    _EMAIL_INFO_URL = "https://api.github.com/user/emails"

    def get_provider(self) -> str:
        return "github"

    def get_authorization_url(self):
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": "user:email",
        }
        return f"{self._AUTHORIZE_URL}?{urllib.parse.urlencode(params)}"

    def get_access_token(self, code) -> str:
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "redirect_uri": self.redirect_uri,
        }
        headers = {"Accept": "application/json"}

        response = requests.post(self._ACCESS_TOKEN_URL, data=data, headers=headers)
        response.raise_for_status()
        resp_json = response.json()

        access_token = resp_json.get("access_token")
        if not access_token:
            raise ValueError("Failed to get access token")
        return access_token

    def get_raw_user_info(self, token):
        headers = {
            "Authorization": f"token {token}",
        }

        response = requests.get(self._USER_INFO_URL, headers=headers)
        response.raise_for_status()
        raw_info = response.json()

        response = requests.get(self._EMAIL_INFO_URL, headers=headers)
        response.raise_for_status()
        email_info = response.json()

        primary_email = next(
            (email for email in email_info if email.get("primary", None)), None
        )

        return {**raw_info, "email": primary_email.get("email")}

    def _transform_user_info(self, raw_info):
        email = raw_info.get(
            "email",
            f"{raw_info.get('id')}+{raw_info.get('login')}@users.no-reply.github.com",
        )
        return OAuthUserInfo(
            id=str(raw_info.get("id")),
            name=str(raw_info.get("name")),
            email=email,
        )
