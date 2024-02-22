import os
import openai
import sqlite3
import collect_article
import pandas as pd

# APIキーの設定（非公開）
os.environ['OPENAI_API_KEY'] = 'YOUR_API_KEY'
#エクセルファイルの取得
articles = pd.read_excel('Articles.xlsx')

# 記事を取得
item = collect_article.get_item('feed/https://feedly.com/f/9wpsTw9xaKJQaCZvLXl5pLkt')
# 記事のURLからコンテンツを取得
content = collect_article.get_contents(item)
# 記事を追加
added_articles = collect_article.add_data(articles, item)
added_articles.to_excel('Articles.xlsx', index=False)
# 元記事の会社名
company = added_articles.iloc[-1]['Company']

# コンテンツの要約
openai.api_type = "azure"
openai.api_base = "MY_API_BASE"
openai.api_version = "2023-07-01-preview"
openai.api_key = os.getenv("OPENAI_API_KEY")

command = f"""\
    #制約条件
    1. Cookieに関する記述がある場合それを無視する
    2. 重要なキーワードを取りこぼさない。
    3. 架空の表現や言葉を使用しない。
    4. 20文字以内の見出しを3つ出力する
    5. 各見出しに関する詳しい内容を150文字以上で出力する
    6. 出力する文章は最大500文字とする
    7. 出力する文章は日本語で出力する

    # 要約する文章
    ----------
    {content[0].dict()["page_content"]}

    # 出力形式
    ## 見出し1
    見出し1の内容
    ## 見出し2
    見出し2の内容
    ## 見出し3
    見出し3の内容

    """

message_text2 = [{"role":"system","content":"あなたは最新技術に詳しい新聞記者です。次の条件に従って、入力する文章を要約してください。"},
                {"role": "user", "content": command}]

responce2 = openai.ChatCompletion.create(
  engine="engine",
  messages = message_text2,
  temperature=0.3,
  max_tokens=5000,
  top_p=0.95,
  frequency_penalty=0,
  presence_penalty=0,
  stop=None
)
summary = responce2["choices"][0]["message"]["content"]
answer ='''
{}
{}

引用元:{}
出典:{}
'''.format(summary, company, item['canonicalUrl'])


directory = 'articles'
filename = (item['title'] + '.md').replace(':', ',')
filepath = os.path.join(directory, filename)

with open(filepath, 'w', encoding='utf-8',) as f:
  f.write(product)