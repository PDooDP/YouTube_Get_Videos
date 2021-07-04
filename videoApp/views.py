from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse
import requests
import pandas as pd
from datetime import datetime
from requests import api
from videoApp.video_class import *
from videoApp.dbConn_class import *

# Create your views here.

# YOUTUBE_API_KEY = "AIzaSyAvE_IYKLSmKPvlz12xVsJdzkMHtzw5DvQ"
# base_url = "https://www.googleapis.com/youtube/v3/"

# 初始化程式
def main():
    global db, yt
    db = dbConn()
    yt = videoRetreiver()

main()

# 首頁
# OK
def videoAppHome (request):
    return render(request, "videoAppHome.html",{})

# 顯示所有的頻道名稱
# OK
def videoShow(request):
    sql = "SELECT * FROM tbl_channel"
    data = db.sql_selectFetchAll(sql)  # 呼叫自訂資料庫函式dbConn內的select all尋找所有的頻道資料
    return render(request, "videoShow.html", {"data": data})

# 取得頻道總影片列表 (可以在更穩定的版本內加入)
# OK
def videoShowDetails(request,playlist_ID=-1):
    # 尋找頻道影片列表內所有影片的ID
    video_ids = yt.YT_videos_getID("details", "contentDetails", playlist_ID)

    # 取得所有的影片ID後，再尋找出影片資訊：標題、點閱數、按讚數、倒讚數等===
    video_infos = yt.YT_videoStats(video_ids,"snippet,statistics")
    return render(request, "videoShowDetails.html", {"video_infos": video_infos})

# 取得資料庫內所有頻道在1日內上傳的最新影片
# 首頁: 今日最新
# OK
def videoShowNewest(request):
    global today_infos
    today_infos = []
    # channel_imgs = []
    # 取得所有在資料庫內的playlist_id, 再呼叫videoTodayHandle取得播放清單內的最新影片
    sql = "SELECT playlist_id FROM tbl_channel"
    data = db.sql_selectFetchAll(sql)

    for i in range(len(data)):
        videoTodayHandle(data[i][0])

    return render(request,"videoShowToday.html", {"today_infos": today_infos})

# 根據選取的頻道找出1日內上傳的最新影片
# 用playlist_ID做搜索條件
# 頻道列表: 今日最新
# OK
def videoShowToday(request,playlist_ID=-1):
    global today_infos
    today_infos = []    # 取得今日影片的資訊
    # channel_imgs = []   # 取得頻道縮圖

    # 搜尋單一頻道的播放清單ID, 再呼叫videoTodayHandle取得該播放清單內的最新影片
    sql = "SELECT playlist_id FROM tbl_channel WHERE playlist_id = '{}'".format(playlist_ID)
    data = db.sql_selectFetchAll(sql)

    for i in range(len(data)):
        videoTodayHandle(data[i][0])
 
    return render(request,"videoShowToday.html", {"today_infos": today_infos})

# 新增頻道表單頁面
# OK
def videoAddForm(request):
    return render(request, "videoForm.html")

# 取得頻道詳細資料 (新增頻道)
# OK
def channelRetreive(request):
    # 從影片清單網址取得playlist_ID
    if request.method == "POST":
        usrInput = request.POST["video_url"]
        # if usrInout != "":
        playlist_id = yt.YT_playlist_getID(usrInput)

    data = yt.YT_playlist_info(playlist_id)

    return render(request,"videoForm.html",{"data": data})

# 將頻道詳細內容寫入資料庫 (新增頻道)
# OK   
def channelInfoDB(request):
    if request.method == "POST":
        channel_title = request.POST["channel_title"]
        channel_ID = request.POST["channel_ID"]
        playlist_ID = request.POST["playlist_ID"]
        channel_img = request.POST["channel_img"]
        playlist_title = request.POST["playlist_title"]
        channel_url = f"https://www.youtube.com/channel/{channel_ID}"

        sql = f"INSERT INTO tbl_channel (channel_id, playlist_id, channel_title, playlist_title, channel_url, channel_img) VALUES ('{channel_ID}','{playlist_ID}','{channel_title}','{playlist_title}','{channel_url}','{channel_img}')"
        
        db.sql_execute(sql)
        message = "已匯入至資料庫"
    return render(request, "videoForm.html", {"message": message})

# 將tbl_channel的pid(id)代入並更新頻道的資訊
# OK
def videoUpdateForm(request,id=-1):
    sql = "SELECT playlist_id FROM tbl_channel WHERE pid_channel = {}".format(id)
    playlist_id = db.sql_selectFetchOne(sql, 0)
    sql = "SELECT * FROM tbl_channel WHERE playlist_id = '{}'".format(playlist_id)
    data = db.sql_selectFetchAll(sql)
    pid = id
    return render(request, "videoUpdateForm.html", {"playlist_id": playlist_id, "data": data, "pid": pid})

# 顯示資料庫內所有頻道的資訊
# OK
def videoEdit(request):
    sql = "SELECT * FROM tbl_channel"
    data = db.sql_selectFetchAll(sql)
    return render(request, "videoEdit.html",{"data": data, "id": id})

# 選擇刪除或修改的程序
# OK
def videoEditActions(request, id=-1):
    if request.method == "POST":
        action = request.POST["actions"]
        if action == "edit":    # 選擇修改
            return redirect("/videoUpdateForm/{}".format(id))
        elif action == "delete":    # 選擇刪除
            return redirect("/videoDelete/{}".format(id))

# 將修改的內容傳回資料庫進行更新
# OK
def videoEditHandle(request, id=-1):
    if request.method == "POST":
        channel_title = request.POST["channel_title"]
        playlist_title = request.POST["playlist_title"]
        sql = f"UPDATE tbl_channel SET channel_title = '{channel_title}', playlist_title = '{playlist_title}' WHERE pid_channel = {id}"
        db.sql_execute(sql)
        return redirect("/videoEdit/")

# 依id做為條件刪除頻道資料
# OK
def videoDelete(id=-1):
    sql = f"DELETE FROM tbl_channel WHERE pid_channel = {int(id)}"
    db.sql_execute(sql)
    return redirect("/videoEdit/")

# 負責將今日影片的ID儲存起來, videoShowToday則只需要用迴圈將channelID代入即可。
# OK
def videoTodayHandle(playlist_ID):
    # 尋找影片清單內所有影片的ID
    video_ids = yt.YT_videos_getID("one","snippet", playlist_ID)

    # 找出的影片ID，尋找出影片資訊：標題、點閱數、按讚數、倒讚數等
    today_Videoinfos = yt.YT_videoStats(video_ids,"snippet,statistics",today_infos)

    return today_Videoinfos
# ===================================================================