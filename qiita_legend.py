import calendar
import json

import requests
from flask import Flask, render_template

# url = 'https://qiita.com'+'/api/v2/authenticated_user/items'

access_token = ''
headers = {'Authorization': 'Bearer '+access_token}

selected_articles = []

target_year = '2021'

for month in ['1']:  # , '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']:
    print('['+month+'月]')  # : ', str(len(json.loads(response.text)))+'個')

    _, lastday = calendar.monthrange(int(target_year), int(month))
    # print(lastday)
    for page in range(1, 2):
        url = 'https://qiita.com/api/v2/items?page='+str(page)+'&per_page=100&query=created%3A%3E'+target_year+'-'+month.zfill(2)+'-01+created%3A%3C'+target_year+'-' + \
            month.zfill(2)+'-'+str(lastday)+'+stocks%3A%3E300'
        # url = 'https://qiita.com/api/v2/items?page='+str(page)+'&per_page=100&query=created%3A%3E2020-08-01+created%3A%3C2020-08-31+stocks%3A%3E500'

        response = requests.get(url, headers=headers)
        # response = requests.get(url)
        selected_articles.append(json.loads(response.text))

        # for i in range(len(json.loads(response.text))):
        #     likes_count = json.loads(response.text)[i]["likes_count"]
        #     title = json.loads(response.text)[i]["title"]
        #     article_url = json.loads(response.text)[i]["url"]
        #     print(str(i+1)+'番目', likes_count, title, article_url)


app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html', title='qiita legend', selected_articles=selected_articles)


if __name__ == "__main__":
    app.run(debug=True, port=8888, threaded=True)

# 実行方法
# python qiita_legend.py
