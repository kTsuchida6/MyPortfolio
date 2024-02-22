import requests
import pandas as pd
import sqlite3
import datetime
from langchain_community.document_loaders import SeleniumURLLoader
import os
import openai


def get_item(ID):
    auth_token='YOUR_AUTH_TOKEN'
    head = {'Authorization': 'Bearer ' + auth_token}

    # FeedlyのAPIエンドポイント
    url = f"https://cloud.feedly.com/v3/streams/contents"

    params = {
    'streamId': ID,
    'count': 1,  # 取得したい記事の数
    }

    response = requests.get(url, headers=head, params=params)
    data = response.json()

    # 記事のURLを出力
    item = data['items'][0]

    return item

#　記事を保存
def add_data(df, data):
    dt_now = datetime.datetime.now()
    now = dt_now.strftime('%Y-%m-%d')
    new_data = {'ID': [data['id']], 'Title': [data['title']], 'URL': [data['canonicalUrl']], 'Company': [data['origin']['title']], 'Date': [now]}
    df_data = pd.DataFrame(new_data)
    new_df = pd.concat([df, df_data], ignore_index=True)
    dup = new_df.duplicated(subset=["ID"], keep="first")
    if (dup.any() == True):
        raise ValueError('Error: This article already exists')
    else:
        return new_df

# データベースに記事を保存
def operate_db(data):
    dt_now = datetime.datetime.now()
    
    dbname = 'Articles.db'
    conn = sqlite3.connect(dbname)
    cur = conn.cursor()
    
    try :
        cur.execute(
            "insert into articles(id, title, url, date) values(?, ?, ?, ?);", 
            (data['id'], data['title'], data['canonicalUrl'], dt_now))
        return 
    
    except sqlite3.IntegrityError as e:
        return e
    
    finally:
        conn.commit()
        cur.close()
        conn.close()

def get_contents(item):
    # URLからコンテンツを取得
    urls = [item['canonicalUrl']]

    loader = SeleniumURLLoader(urls=urls)
    data = loader.load()

    return data
