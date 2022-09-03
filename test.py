from api import AltoTikTokApi
from dataclasses import asdict, dataclass, is_dataclass
import logging
import json
import csv
import xlsxwriter

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
        with open(f"{self.hashtag}.csv", 'w', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)
            
            header = ["id", "desc", "hashtags", "playAddr"]
            writer.writerow(header)
            for entry in self.videos:
                if is_dataclass(entry):
                    entry = asdict(entry)
                writer.writerow(
                    [
                        entry.get("id", ""),
                        entry.get("desc", ""),
                        ", ".join(h["name"] for h in entry.get("hashtags", [])),
                        entry.get("playAddr", ""),
                        
                    ]
                )    
    
    def _write_xls_row(self, workbook, worksheet, row_data, row_num, is_header=False):
        '''
            worksheet: xlsxwriter worksheet
            row_data: list[str]
            row_num: int
        '''
        cell_format = workbook.add_format()
        if is_header:
            cell_format.set_bold(True)
        for idx, entry in enumerate(row_data):
                            # row  column  val
            worksheet.write(row_num, idx, entry, cell_format)
    
    def _dump_xlsx_raw_data(self, workbook):
        header = ["id", 
                  "desc", 
                  "hashtags",
                  "playCount",
                  "shareCount",
                  "commentCount",
                  "playAddr"
                  ]
        worksheet = workbook.add_worksheet('Data')
        worksheet.set_column('A:A', 25) 
        worksheet.set_column('B:B', 60) 
        worksheet.set_column('C:C', 50)
        worksheet.set_column('D:D', 15) 
        worksheet.set_column('E:E', 15) 
        worksheet.set_column('F:F', 10) 
        worksheet.set_column('G:G', 15)
         
        
        self._write_xls_row(workbook, worksheet, header,0, True)
        
        def get_play_address_hyperlink(play_address):
            if not play_address:
                return ""
            return f'=HYPERLINK("{play_address}", "Video Link")'
        
        for idx, entry in enumerate(self.videos):
            if is_dataclass(entry):
                entry = asdict(entry)
            stats = entry.get("stats")
            if is_dataclass(stats):
                stats = asdict(stats)
                
            self._write_xls_row(
                workbook,
                worksheet,
                [
                    entry.get("id", ""),
                    entry.get("desc", ""),
                    ", ".join(h["name"] for h in entry.get("hashtags", [])),
                    stats.get("playCount",""),
                    stats.get("shareCount",""),
                    stats.get("commentCount",""),
                    get_play_address_hyperlink(entry.get("playAddr","")),
                ],
                idx + 1
            )

    def _dump_xlsx_occurrences(self, workbook):
        test = {'total': 483, 
                'top_n': [
                    ['toronto', 'fyp', 'foryou', 'foryoupage', 'canada', 'viral', 'fypシ', 'haircut', 'ontario', 'comedy'], 
                          [483, 263, 103, 92, 76, 55, 41, 34, 31, 31]]
                }
        worksheet = workbook.add_worksheet('Occurrences')
        worksheet.set_column('A:A', 15) 
        worksheet.set_column('B:B', 15) 
        worksheet.set_column('C:C', 15)
        worksheet.set_column('D:D', 15) 
        header = ["Rank", 
                  "Hashtag", 
                  "Occurrences",
                  "Frequency",
                  ]
        occurrences_data= self.get_occurrences()
        self._write_xls_row(workbook, worksheet, header,0, True)
        for idx, hashtag in enumerate(occurrences_data["top_n"][0]):
            occurrences = occurrences_data["top_n"][1][idx]
            self._write_xls_row(
                workbook,
                worksheet,
                [
                    idx,
                    hashtag,
                    occurrences,
                    occurrences/occurrences_data["total"],
                ],
                idx+1,
            )

        chart = workbook.add_chart({'type': 'column'})
        chart.add_series({
            'values': '=$Occurrences!$D$2:$D$11',
        })
        worksheet.insert_chart('G3', chart)
        
    def export_xlsx(self):
        workbook = xlsxwriter.Workbook(f'{self.hashtag}.xlsx')
        self._dump_xlsx_occurrences(workbook)
        self._dump_xlsx_raw_data(workbook)
        workbook.close()
    
if __name__ == "__main__":
    hashtag = "toronto"
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
    print(res.get_occurrences())
    res.export_xlsx()
    res.print_occurrences()
