from dataclasses import asdict, dataclass, is_dataclass
from tkinter import Y
from turtle import down
from TikTokApi import TikTokApi
from TikTokApi.exceptions import TikTokException
import logging
import json
import csv
import random 
import string
import sys

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
    create_time: str
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
    token = ""
    def __init__(self, hashtag=None, user=None, token=None):
        super().__init__()
        
        if not hashtag and not user:
            raise ValueError("Must provide either a user or a hashtag kwarg")
        if hashtag and user:
            raise ValueError("Please provide only one of user or hashtag as a kwarg")
            
        
        self.hashtag = hashtag
        self.user = user
        self.token = token
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

    def get_videos(self, download=False):
        api = TikTokApi(logging_level=logging.ERROR, custom_verify_fp=self.token, force_verify_fp_on_cookie_header=True)
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
            try:
                info = video.info()
                author = video.as_dict["author"]
                sound=video.as_dict["music"]
                tiktok_video = TikTokVideo(
                    id=video.id,
                    desc=info["desc"],
                    create_time=str(video.create_time),
                    hashtags=[TikTokHashtag(id=h.id,name=h.name ) for h in video.hashtags],
                    playAddr=info["video"].get("playAddr"),
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
                
                if download:
                    self.download_video(video)
                
                self.videos = res
                with open(f'{self.filename}.json', 'w') as outfile:
                    json.dump(res, outfile, cls=EnhancedJSONEncoder)
            except TikTokException as e:
                print(f"Error Processing Video: {video.id} continuing anyway")    
    def download_video(self, video):
       try:
            video_data = video.bytes()
            video_name = video.id
            with open(f"{video_name}.mp4", "wb") as out_file:
                out_file.write(video_data)
       except TikTokException as e:
           print(f"Error Processing Video: {video.id} continuing anyway")    
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
                    "Create Time"
                    # Author Info
                    "Author Id",
                    "Author",
                    "Author Nickname",
                    "Author Verified",
                    # Sound,
                    "Sound ID",
                    "Sound Name",
                    "Sound Artist",
                    "Sound Original",
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
                        entry.get("create_time", ""),
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
    token=""
    print("###########################################")
    print("#            TIK TOK SCRAPER              #")
    print("###########################################")
    print("       Press Ctrl+C/ Cmd+C to Exit         ")
    print()
    
    while not token:
        print("Enter your `s_v_web_id` cookie. see Readme.md for instructions on how to get this value")
        val =input("s_v_web_id: ")
        if val:
            token = val
        print()
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
    if search_type == "H":
        results = TikTokHashTagAnalyzer(hashtag=search_term, token=token)
    elif search_type == "U":
        results = TikTokHashTagAnalyzer(user=search_term, token=token)    
    try:
        with open(f'{search_type}_{search_term}.json') as json_file:
            print(f"Previous Data Found for Search Type {search_type}/ Search Term {search_term}")
            print("Rerun analysis on this data?")
            rerun = None
            while rerun is None:
                val = input("Y/N")
                if val == "Y":
                    rerun = True
                elif val == "N":
                    rerun = False
            if rerun:
                data = json.load(json_file)
                results.videos = data
                if not data:
                    results.get_videos()
            else:
                should_download = None
                while should_download is None:
                    print("Should Videos be Downloaded? (This May Take a While)")
                    val = input("Y/N: ")
                    
                    if val == "Y":
                        should_download = True
                    elif val == "N":
                        should_download = False
                results.get_videos(download=should_download)
    except FileNotFoundError:
        should_download = None
        while should_download is None:
            print("Should Videos be Downloaded? (This May Take a While)")
            val = input("Y/N: ")
            if val == "Y":
                should_download = True
            elif val == "N":
                should_download = False
        results.get_videos(download=should_download)
    results.get_hashtags()
    results.to_csv()
    results.print_occurrences()
    sys.exit()