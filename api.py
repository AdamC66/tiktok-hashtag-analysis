
from TikTokApi import TikTokApi
from dataclasses import asdict, dataclass, is_dataclass
from typing import List
import random
from http import cookiejar
from urllib.parse import quote, urlencode
from TikTokApi import TikTokApi
from TikTokApi.api.user import User
from TikTokApi.browser_utilities.browser import browser


async def patch_create_context(self, set_useragent=False):
    iphone = self.playwright.devices["iPhone 11 Pro"]
    iphone["viewport"] = {
        "width": random.randint(320, 1920),
        "height": random.randint(320, 1920),
    }
    iphone["device_scale_factor"] = random.randint(1, 3)
    iphone["is_mobile"] = random.randint(1, 2) == 1
    iphone["has_touch"] = random.randint(1, 2) == 1

    iphone["bypass_csp"] = True
    iphone["ignore_https_errors"] = True

    context = await self.browser.new_context(**iphone)
    if set_useragent:
        self.user_agent = iphone["user_agent"]

    return context


def patch_user_info_full(self, **kwargs) -> dict:
    """
    Returns a dictionary of information associated with this User.
    Includes statistics about this user.

    Example Usage
    ```py
    user_data = api.user(username='therock').info_full()
    ```
    """

    # TODO: Find the one using only user_id & sec_uid
    if not self.username:
        raise TypeError(
            "You must provide the username when creating this class to use this method."
        )

    quoted_username = quote(self.username)
    query = {
        "uniqueId": quoted_username,
        "secUid": "",
        "msToken": User.parent._get_cookies(**kwargs)["msToken"],
    }
    path = f"api/user/detail/?{User.parent._add_url_params()}&{urlencode(query)}"
    res = User.parent.get_data(path, subdomain="m", **kwargs)
    return res["userInfo"]


class AltoTikTokApi(TikTokApi):
    cookie_file: str

    def __init__(self, *args, cookie_file: str = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.cookie_file = cookie_file
        self._load_cookies_from_file()

    def _load_cookies_from_file(self):
        if self.cookie_file is None:
            self.cookies = {}
        else:
            cookie_jar = cookiejar.MozillaCookieJar(self.cookie_file)
            cookie_jar.load()
            self.cookies = {cookie.name: cookie.value for cookie in cookie_jar}

    def _get_cookies(self, **kwargs):
        # final_cookies = dict(self.cookies)
        # final_cookies.update(kwargs)
        # return final_cookies
        return self.cookies

    def get_cookie_file_name(self) -> str:
        return self.cookie_file


browser._create_context = patch_create_context
AltoTikTokApi.user.info_full = patch_user_info_full
