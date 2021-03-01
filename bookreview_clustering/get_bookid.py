import requests
from bs4 import BeautifulSoup
import time
import datetime
import logging

dt_now = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
#logging.basicConfig(filename=f'{dt_now}_get_bookid.log', level=logging.INFO)

bookid_list = []
for pagenum in range(50):
    print(pagenum)
    # 2020年の登録数ランキング
    url = f"https://booklog.jp/ranking/annual/2020/book?page={pagenum+1}&sort=users"
    s = requests.Session()
    r = s.get(url)
    soup = BeautifulSoup(r.text)

    time.sleep(3)

    books = soup.find_all("div", class_="thumb")
    for book in books:
        bookid = book.find("a").get("href")
        # 保存
        with open(f"csvfile/bookid_list_{dt_now}.csv", mode='a') as f:
            f.write(bookid)
            f.write("\n")
