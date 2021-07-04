"""project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import url
from myapp.views import *
from videoApp.views import *

# 使用正規法比較方便, 比起書上採用的path語法
# 改用url會更有效率
urlpatterns = [
    # path(r'^admin/', admin.site.urls),
    # path(r'videoAppHome/', videoAppHome),
    # url(r'^admin/$', admin.site.urls),
    url(r'^myapp/$', myAppHome),
    # url(r'^base/$', base),  # 網頁模板
    url(r'^videoAppHome/$', videoAppHome),  # 首頁
    # url(r'^videoHandle/$', videoHandle),
    url(r'^channelRetreive/$', channelRetreive),    # 取得表單資料
    url(r'^channelInfoDB/$', channelInfoDB),        # 新增頻道資訊至資料庫
    url(r'^videoShow/$', videoShow),                # 顯示頻道列表
    url(r'^videoShowDetails/(\w.+)$', videoShowDetails), # 取得頻道所有的影片 (不建議使用)
    url(r'^videoShowToday/(\w.+)$', videoShowToday),    # 取得單一頻道的最新影片
    url(r'^videoShowToday/$', videoShowNewest),         # 取得資料庫內所有頻道的最新影片
    url(r'^videoAddForm/$', videoAddForm),  # 新增頻道頁面
    url(r'^videoUpdateForm/(\w+)$', videoUpdateForm),   # 修改頻道資訊的表單
    url(r'^videoEdit/$', videoEdit),    # 進入修改頻道的頁面
    url(r'^videoEditActions/(\w+)$', videoEditActions),    # 選擇修改或刪除的程序
    url(r'^videoEditHandle/(\w+)$', videoEditHandle),      # 處理修改的程序並傳到資料庫
    url(r'^videoDelete/(\w+)$', videoDelete),
    # url(r'^videoMessage/$', videoMessage),
]
