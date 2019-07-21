import pandas as pd
import time
import itertools

initflag=1
for year, league in itertools.product(range(2014, 2019), ['p', 'c']):
    url=f'http://npb.jp/bis/{year}/stats/bat_{league}.html'
    tables = pd.read_html(url)
    df_with_header = tables[0]
    df = df_with_header.iloc[2:,:] #使用カラム
    df.columns=df_with_header.iloc[1,:] #列名
    df["year"]=year
    df["league"]=league
    if initflag==1:
        output=df
        initflag=0
    else:
        output=pd.concat([output,df])
    time.sleep(1)

output.to_csv("baseball_stats.csv",index=False)

