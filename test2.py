import string
from TikTokApi import TikTokApi
from dataclasses import asdict, dataclass, is_dataclass
from typing import List
import sys
import logging
from pprint import pprint
import random
from http import cookiejar
from urllib.parse import quote, urlencode
import json
from TikTokApi import TikTokApi
from TikTokApi.api.user import User
from TikTokApi.browser_utilities.browser import browser

class EnhancedJSONEncoder(json.JSONEncoder):
        def default(self, o):
            if is_dataclass(o):
                return asdict(o)
            return super().default(o)


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


@dataclass
class VideoStats:
    diggCount: int
    shareCount: int
    commentCount: int
    playCount: int

@dataclass
class TikTokHashtag:
    id: str
    name: str

@dataclass
class TikTokVideo:
    id: str
    desc: str
    hashtags: list[TikTokHashtag]
    stats: VideoStats
    playAddr: str


class TikTokHashTagAnalyzer(object):
    
    hashtag = ""
    videos = []
    tags = []
    tag_occurrences = []
    video_count = 3000
    def __init__(self, hashtag):
        super().__init__()
        self.hashtag = hashtag
    def get_hashtags(self):
        if not self.videos:
            raise ValueError(f"Empty videos, run get_videos() first, no hashtags could be extracted.")
        hashtags = {}
        tags = [set([tag.name for tag in ele.hashtags]) for ele in self.videos]
        {
            tag: (
                1
                if tag not in hashtags and not hashtags.update({tag: 1})
                else hashtags[tag] + 1 and not hashtags.update({tag: hashtags[tag] + 1})
            )
            for ele in tags
            for tag in ele
        }
        
        self.tags = sorted(hashtags.items(), key=lambda e: e[1], reverse=True)
        return sorted(hashtags.items(), key=lambda e: e[1], reverse=True)

    def get_videos(self):
        if not self.hashtag:
            raise ValueError("Hashtag must be given")
        api = AltoTikTokApi(logging_level=logging.ERROR, cookie_file="cookies.txt")
        tag = api.hashtag(name=self.hashtag)
        videos = [v for v in tag.videos(count=self.video_count)]
        res = []
        for idx, video in enumerate(videos):
            if idx % 30 == 0:
                if idx == 0:
                    print("Processing . . .")
                else:
                    print(f"{idx} Videos processed")
            info = video.info()
            tiktok_video = TikTokVideo(
                id=video.id,
                desc=info["desc"],
                hashtags=[TikTokHashtag(id=h.id,name=h.name ) for h in video.hashtags],
                playAddr=info["video"]['playAddr'],
                stats=VideoStats(**video.stats)
            )
            res.append(tiktok_video)
        self.videos = res
        with open(f'{self.hashtag}.json', 'w') as outfile:
            json.dump(res, outfile, cls=EnhancedJSONEncoder)
        
    def get_occurrences(self):
        occs = {"total": len(self.videos), "top_n": []}
        occs["top_n"] = [[ele[i] for ele in self.tags[0 : min(len(self.videos), 10)]] for i in range(2)]
        self.tag_occurrences = occs

    def print_occurrences(self):
        """Print information about the top n hashtags and their frequencies."""
        self.get_occurrences()
        row_number = 0
        total_posts = self.tag_occurrences["total"]
        print(
            "{:<8} {:<30} {:<15} {:<15}".format(
                "Rank", "Hashtag", "Occurrences", "Frequency"
            )
        )
        for key, value in zip(self.tag_occurrences["top_n"][0], self.tag_occurrences["top_n"][1]):
            ratio = value / total_posts
            print("{:<8} {:<30} {:<15} {:.4f}".format(row_number, key, value, ratio))
            row_number += 1
        print(f"Total posts: {total_posts}")

if __name__ == "__main__":
    hashtag = "london"
    res = TikTokHashTagAnalyzer(hashtag)
    try:
        with open(f'{hashtag}.json') as json_file:
            data = json.load(json_file)
            res.videos = data
        if not data:
            res.get_videos()
    except FileNotFoundError:
        res.get_videos()
    res.get_hashtags()
    res.print_occurrences()
