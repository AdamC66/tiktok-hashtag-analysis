from dataclasses import asdict, dataclass, is_dataclass
from tkinter import Y
from TikTokApi import TikTokApi
import logging
import json
import csv
import random 
import string

# ###########################################
#            SETUP INSTRUCTIONS
# ###########################################

# Go to www.tiktok.com
# login if you are not. logout and log back in if you are
# Right click on the page and select "Inspect"
# In the Inspector, Click "Application" in the top toolbar
# On the left side under "Storage" select "Cookies", then "https://www.tiktok.com"
# Copy the value of cookie "s_v_web_id" (it should start with "verify_"), and paste it below
# DO NOT COMMIT THIS TOKEN

ms_token="verify_l89fyzfr_0VK1rBdz_wpUW_4lhi_8FXL_fcal1HUqpLra"

# ###########################################   
# ###########################################

class EnhancedJSONEncoder(json.JSONEncoder):
        def default(self, o):
            if is_dataclass(o):
                return asdict(o)
            return super().default(o)

@dataclass
class VideoStats:
    diggCount: int
    shareCount: int
    commentCount: int
    playCount: int

@dataclass
class VideoSound:
    id: int
    title: str 
    authorName: str 
    original: bool 
    playUrl: str 
                

@dataclass
class VideoAuthor:
    id: int
    uniqueId: str
    nickname: str
    verified: bool
    
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
    author: VideoAuthor
    sound: VideoSound

class TikTokHashTagAnalyzer(object):
    
    hashtag = ""
    videos = []
    tags = []
    tag_occurrences = []
    video_count = 5000
    filename = "none"
    
    def __init__(self, hashtag=None, user=None):
        super().__init__()
        
        if not hashtag and not user:
            raise ValueError("Must provide either a user or a hashtag kwarg")
        if hashtag and user:
            raise ValueError("Please provide only one of user or hashtag as a kwarg")
            
        
        self.hashtag = hashtag
        self.user = user
        
        self.filename = ""
        self.filename += "U" if user else "H"
        self.filename += f"_{hashtag or user}"
        
    def get_hashtags(self):
        if not self.videos:
            raise ValueError(f"Empty videos, run get_videos() first, no hashtags could be extracted.")
        hashtags = {}
        try:
            tags = [set([tag.name for tag in ele.hashtags]) for ele in self.videos]
        except AttributeError:
            tags = [set([tag["name"] for tag in ele["hashtags"]]) for ele in self.videos]
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
        api = TikTokApi(logging_level=logging.ERROR, custom_verify_fp=ms_token, force_verify_fp_on_cookie_header=True)
        if self.hashtag:
            tag = api.hashtag(name=self.hashtag)
            videos = [v for v in tag.videos(count=self.video_count)]
        elif self.user:
            user = api.user(username=self.user)
            videos = [v for v in user.videos(count=self.video_count)]
        res = []
        for idx, video in enumerate(videos):
            if idx % 30 == 0:
                if idx == 0:
                    print("Processing . . .")
                else:
                    print(f"{idx} Videos processed")
            info = video.info()
            author = video.as_dict["author"]
            sound=video.as_dict["music"]
            
            tiktok_video = TikTokVideo(
                id=video.id,
                desc=info["desc"],
                hashtags=[TikTokHashtag(id=h.id,name=h.name ) for h in video.hashtags],
                playAddr=info["video"]['playAddr'],
                stats=VideoStats(**video.stats),
                author=VideoAuthor(
                    id= author.get("id"),
                    uniqueId = author.get("uniqueId"),
                    nickname= author.get("nickname"),
                    verified=author.get("verified"),
                ),
                sound=VideoSound(
                    id=sound.get("id"),
                    title= sound.get("title"),
                    authorName= sound.get("authorName"),
                    original= sound.get("original"),
                    playUrl= sound.get("playUrl"),
                )
            )
            res.append(tiktok_video)
        self.videos = res
        with open(f'{self.hashtag}.json', 'w') as outfile:
            json.dump(res, outfile, cls=EnhancedJSONEncoder)
        
    def get_occurrences(self):
        occs = {"total": len(self.videos), "top_n": []}
        occs["top_n"] = [[ele[i] for ele in self.tags[0 : min(len(self.videos), 10)]] for i in range(2)]
        self.tag_occurrences = occs
        return occs

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

    def to_csv(self):
        with open(f"{self.filename}.csv", 'w', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)
            
            header = [
                    # Video Info
                    "Video Id", 
                    "Description", 
                    "Hashtags",
                    # Author Info
                    "Author Id",
                    "Author",
                    "Author Nickname",
                    "Author Verified",
                    # Sound,
                    "Sound ID",
                    "Sound Name",
                    "Sound Artist",
                    "Sound Original"
                    # Stats
                    "Play Count",
                    "Share Count",
                    "Comment Count",
                    # Links
                    "Play Address",
                    "Sound Url"
                  ]
            writer.writerow(header)
            for entry in self.videos:
                if is_dataclass(entry):
                    entry = asdict(entry)
                stats = entry.get("stats")
                author = entry.get("author")
                sound = entry.get("sound")
                writer.writerow(
                    [
                        entry.get("id", ""),
                        entry.get("desc", ""),
                        ", ".join(h["name"] for h in entry.get("hashtags", [])),
                        
                        author.get("id"),
                        author.get("uniqueId"),
                        author.get("nickname"),
                        author.get("verified"),
                        
                        sound.get("id"),
                        sound.get("title"),
                        sound.get("authorName"),
                        sound.get("original"),
                    
                        stats.get("playCount",""),
                        stats.get("shareCount",""),
                        stats.get("commentCount",""),
                        entry.get("playAddr", ""),
                        sound.get("playUrl"),
                    ]
                )    
    
    
if __name__ == "__main__":
    search_type=""
    search_term=""
    print("###########################################")
    print("#            TIK TOK SCRAPER              #")
    print("###########################################")
    print("       Press Ctrl+C/ Cmd+C to Exit         ")
    print()    
    while not search_type:
        print("Lookup By User(U) or HashTag(H)")
        val =input("H / U? : ")
        if val == "H" or val == "U":
            search_type = val
        print()
    print()
    while not search_term:
        print("Enter Search Term")
        val =input("Search : ")
        search_term = val
    print()

    hashtag = "italy"
    if search_type == "H":
        results = TikTokHashTagAnalyzer(hashtag=search_term)
    elif search_type == "U":
        results = TikTokHashTagAnalyzer(user=search_term)
        
    try:
        with open(f'{search_type}_{search_term}.json') as json_file:
            print(f"Previous Data Found for Search Type {search_type}/ Search Term {search_term}")
            print("Rerun analysis on this data?")
            rerun = None
            while rerun is None:
                input("Y/N")
                if input == "Y":
                    rerun = True
                elif input == "N":
                    rerun = False
            if rerun:
                data = json.load(json_file)
                results.videos = data
                if not data:
                    results.get_videos()
            else:
                results.get_videos()
    except FileNotFoundError:
        results.get_videos()
    results.get_hashtags()
    print(results.get_occurrences())
    results.to_csv()
    results.print_occurrences()