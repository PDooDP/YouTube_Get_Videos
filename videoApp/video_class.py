import requests
import re
from datetime import datetime

class videoRetreiver():
    def __init__(self):
        self.base_url = "https://www.googleapis.com/youtube/v3/"
        self.YOUTUBE_API_KEY = "AIzaSyAvE_IYKLSmKPvlz12xVsJdzkMHtzw5DvQ"

    # === 取得json資料 ===
    def loadJson(self,url):
        data = requests.get(url)
        data.encoding = "utf-8"
        data = data.json()
        return data

    # === 取得頻道channel ID ===
    def YT_channel_getID(self, playlist_id, maxResults = 20, part_text = "snippet"):
        playlist_url = f"{self.base_url}playlistItems?part={part_text}&playlistId={playlist_id}&maxResults={maxResults}&key={self.YOUTUBE_API_KEY}"

        ret_list = self.loadJson(playlist_url)
        channel_ID = ret_list["items"][0]["snippet"]["channelId"]
        return channel_ID

    # === 分析URL並取得playlistId ===
    def YT_playlist_getID(self, yt_url):
        chkPattern = "&index"
        pattern1 = "list=(.*)&index"    # verified account
        pattern2 = "list=(.*)"          # regular account
        chk = re.search(chkPattern, yt_url)   # identify account type
        if chk == None:
            txt = re.search(pattern2, yt_url)
        else:
            txt = re.search(pattern1, yt_url)

        playlist_ids = txt.groups()
        Id = playlist_ids[0]
        return Id

    # === 取得播放清單名稱 ===
    # https://youtube.googleapis.com/youtube/v3/playlists?part=snippet&id=UUVizi411ybhS3LKxX6DocDA&maxResults=20&key=AIzaSyAvE_IYKLSmKPvlz12xVsJdzkMHtzw5DvQ
    def YT_playlist_title(self, playlist_id, part_text = "snippet"):
        playlist_url = f"{self.base_url}playlists?part={part_text}&id={playlist_id}&key={self.YOUTUBE_API_KEY}"

        # ==== 找數量 ====
        ret_list = self.loadJson(playlist_url)
        playlist_title = ret_list["items"][0]["snippet"]["title"]
        
        return playlist_title

    # === 取得播放清單Playlist資料 ===
    # 包含播放清單名稱
    def YT_playlist_info(self, playlist_id, maxResults = 20, part_text = "snippet"):
        playlist_url = f"{self.base_url}playlistItems?part={part_text}&playlistId={playlist_id}&maxResults={maxResults}&key={self.YOUTUBE_API_KEY}"

        ret_list = self.loadJson(playlist_url)
        channel_title = ret_list["items"][0]["snippet"]["channelTitle"]
        channel_ID = ret_list["items"][0]["snippet"]["channelId"]
        totalResult = ret_list["pageInfo"]["totalResults"]
        playlist_ID = ret_list["items"][0]["snippet"]["playlistId"]

        img_url = f"{self.base_url}channels?part={part_text}&id={channel_ID}&key={self.YOUTUBE_API_KEY}"
        playlist_title = self.YT_playlist_title(playlist_id)

        ret_img = self.loadJson(img_url)
        channel_img = ret_img["items"][0]["snippet"]["thumbnails"]["default"]["url"]

        data = {}
        data = {
                "channel_title": channel_title,
                "channel_ID": channel_ID,
                "totalResult": totalResult,
                "playlist_ID": playlist_ID,
                "channel_img": channel_img,
                "playlist_title": playlist_title,
        }
        return data

    # === 取得今日影片Videos id ===
    # status須代入: 1. one = 今日 ; 2. details = 所有的影片
    def YT_videos_getID(self, status, part_text, playlist_id, maxResults = 20):
        maxResults = 20
        # base_url = "https://www.googleapis.com/youtube/v3/"
        video_ids = []
        playlist_url = f"{self.base_url}playlistItems?part={part_text}&playlistId={playlist_id}&maxResults={maxResults}&key={self.YOUTUBE_API_KEY}"

        ret_list = self.loadJson(playlist_url)
        next_url = ""
        totalResult = ret_list["pageInfo"]["totalResults"]
        chkToday = False
        date_format = "%Y-%m-%d"
        get_today = datetime.strptime(datetime.today().strftime("%Y-%m-%d"), date_format)
        num = 0

        # 若紀錄超過maxResults, 則需要分頁並取得下一頁的nextPageToken的名稱
        # 由於最後一頁沒有nextPageToken, 所以取商就好
        if int(totalResult % maxResults) != 0:
            num = int(totalResult/maxResults) + 1
        else:
            num = int(totalResult/maxResults)
        
        # 搜出所有的影片ID
        # 用while搜出1天內上傳的影片
        # 如果影片數量少於totalResults, 則不會出現nextPageToken欄位
        # ======================================================
        if status == "one": # 只取得今日最新影片
            if "nextPageToken" not in ret_list:
                while chkToday != True:
                    for i in range(len(ret_list["items"])):
                        # 找出1天內上傳的影片
                        video_date = datetime.strptime(ret_list["items"][i]["snippet"]["publishedAt"][:10], date_format)
                        if (get_today - video_date).days > 1:
                            chkToday = True # 超過一天則跳出while迴圈
                        else:
                            video_ids.append(ret_list["items"][i]["snippet"]["resourceId"]["videoId"])
                            next_url = "{}playlistItems?part={}&playlistId={}&maxResults={}&key={}".format(self.base_url,part_text,playlist_id,maxResults,self.YOUTUBE_API_KEY) 
            else:   # 如果json內有nextPageToken欄位
                next_tokens = ret_list["nextPageToken"]
                for j in range(num):
                    while chkToday != True:
                        if next_url is not "":
                            ret_list = self.loadJson(next_url)
                            # 如果nextPageToken有出現才會抓新的Token, 因為最後一頁不會顯示nextPageToken欄位
                            if "nextPageToken" in ret_list:    
                                next_tokens = ret_list["nextPageToken"]
                        for i in range(len(ret_list["items"])):
                            # 找出1天內上傳的影片
                            video_date = datetime.strptime(ret_list["items"][i]["snippet"]["publishedAt"][:10], date_format)
                            if (get_today - video_date).days > 1:
                                chkToday = True # 超過一天則跳出while迴圈
                            else:
                                video_ids.append(ret_list["items"][i]["snippet"]["resourceId"]["videoId"])
                                next_url = "{}playlistItems?part={}&playlistId={}&maxResults={}&pageToken={}&key={}".format(self.base_url,part_text,playlist_id,maxResults,next_tokens,self.YOUTUBE_API_KEY)
        # =======================================================
        elif status == "details":   # 取得頻道(播放清單)內所有的影片
            if "nextPageToken" not in ret_list:
                for i in range(len(ret_list["items"])): # 先取得第一頁的影片資料, 並將新的nextPageToken放入next_url變數後, 再呼叫新的json資料進來
                    video_ids.append(ret_list["items"][i]["contentDetails"]["videoId"])
                    next_url = f"{self.base_url}playlistItems?part={part_text}&playlistId={playlist_id}&maxResults={maxResults}&key={self.YOUTUBE_API_KEY}"
            else:
                next_tokens = ret_list["nextPageToken"]
                for j in range(num):
                    if next_url is not "":  # 第二頁的影片資料
                        ret_list = self.loadJson(next_url)
                        if "nextPageToken" in ret_list:
                            next_tokens = ret_list["nextPageToken"]
                    for i in range(len(ret_list["items"])):
                        video_ids.append(ret_list["items"][i]["contentDetails"]["videoId"])
                        next_url = f"{self.base_url}playlistItems?part={part_text}&playlistId={playlist_id}&maxResults={maxResults}&pageToken={next_tokens}&key={self.YOUTUBE_API_KEY}"
        return video_ids

    # === 取得影片統計資料 ===
    # 取得影片ID，尋找出影片資訊：標題、點閱數、按讚數、倒讚數等
    def YT_videoStats(self,video_ids, part_text, today_infos=[]):
        for i in range(len(video_ids)):
            video_id = video_ids[i]
            video_url = f'{self.base_url}videos?part={part_text}&id={video_id}&key={self.YOUTUBE_API_KEY}'

            ret_video = self.loadJson(video_url)

            # 將取得的資料儲存成字典型態
            # datetime.strptime將日期和時間格式化
            title = ret_video["items"][0]["snippet"]["title"]
            channel_title = ret_video["items"][0]["snippet"]["channelTitle"]
            date = datetime.strptime(ret_video["items"][0]["snippet"]["publishedAt"], '%Y-%m-%dT%H:%M:%SZ')
            video_img = ret_video["items"][0]["snippet"]["thumbnails"]["medium"]["url"]
            # 取得影片的統計資料
            stat = ret_video["items"][0]["statistics"]

            commentCount = stat["commentCount"]
            likeCount = stat["likeCount"]
            dislikeCount = stat["dislikeCount"]
            viewCount = stat["viewCount"]

            video_info = {
                        "video_ID": video_id,
                        "video_img": video_img,
                        "title": title,
                        "date": date,
                        "viewCount": viewCount,
                        "like": likeCount,
                        "dislike": dislikeCount,
                        "comments": commentCount,
                        "channel_title": channel_title, }
            today_infos.append(video_info)
        return today_infos

    # === 取得影片縮圖 ===
    # === video_id以陣列方式儲存 ===
    # === disabled ===
    # def YT_videosImg(self, video_ids= [], part_text = "snippet,statistics", video_imgs = []):
        # for i in range(len(video_ids)):
        #     video_id = video_ids[i]
        #     video_url = f'{self.base_url}videos?part={part_text}&id={video_id}&key={self.YOUTUBE_API_KEY}'

        #     ret_video = videoRetreiver.loadJson(video_url)

        #     # 將取得的資料儲存成字典型態
        #     # datetime.strptime將日期和時間格式化
        #     video_img = ret_video["items"][0]["snippet"]["thumbnails"]["medium"]["url"]

        #     video_img = {
        #                 "video_img": video_img
        #                                         }
        #     video_imgs.append(video_img)
            # return video_imgs

    # === 頻道影片總數 ===
    def YT_totalVideo(self, playlist_id, maxResults = 20,part_text = "snippet"):
        
        playlist_url = f"{self.base_url}playlistItems?part={part_text}&playlistId={playlist_id}&maxResults={maxResults}&key={self.YOUTUBE_API_KEY}"

        ret_list = self.loadJson(playlist_url)
        totalResult = ret_list["pageInfo"]["totalResults"]
        
        return totalResult
    
# if __name__ == "__main__":
#     main()