import requests
from bs4 import BeautifulSoup
import time
import datetime
import logging
import csv

dt_now = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
bookid_list_path = "csvfile/bookid_list_20210213_114602.csv"
#base_url = "https://booklog.jp"

with open(bookid_list_path) as f:
    bookid_list = f.readlines()

for bookid in bookid_list:
    # リストに改行コードがあるため
    bookid = bookid.replace('\n', '')
    url = f"https://booklog.jp{bookid}?perpage=999&rating=0&is_read_more=1&sort=1"
    print(bookid)
    s = requests.Session()
    r = s.get(url)
    soup = BeautifulSoup(r.text)

    time.sleep(3)

    comments = soup.find_all("p", class_="review-txt")
    title = soup.find("h1", itemprop="name").text
    for comment in comments:
        comment_t = comment.text
        # 保存
        with open(f"csvfile/comment_list_{dt_now}.csv", mode='a') as f:
            writer = csv.writer(f)
            writer.writerow([title, comment_t])
