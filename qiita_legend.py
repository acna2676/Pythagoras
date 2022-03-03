import calendar
import datetime
import json

import requests
from dateutil.relativedelta import relativedelta
from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def index():
    # url = 'https://qiita.com'+'/api/v2/authenticated_user/items'
    with open('access_token.json') as f:
        df = json.load(f)

    access_token = df['access_token']
    headers = {'Authorization': 'Bearer '+access_token}

    selected_articles = []

    dt_now = datetime.datetime.now()
    dt_prev_year = str((dt_now - relativedelta(months=1)).year)
    dt_prev_month = str((dt_now - relativedelta(months=1)).month)
    dt_next_year = str((dt_now + relativedelta(months=1)).year)
    dt_next_month = str((dt_now + relativedelta(months=1)).month)

    target_year = str(dt_now.year)  # '2021'
    target_month = str(dt_now.month)  # '3'

    _, lastday = calendar.monthrange(int(target_year), int(target_month))
    # print(lastday)
    for page in range(1, 2):
        url = 'https://qiita.com/api/v2/items?page='+str(page)+'&per_page=100&query=created%3A%3E'+target_year+'-'+target_month.zfill(2)+'-01+created%3A%3C'+target_year+'-' + \
            target_month.zfill(2)+'-'+str(lastday)+'+stocks%3A%3E30'

        response = requests.get(url, headers=headers)
        selected_articles.append(json.loads(response.text))

    return render_template('index.html', title='Qiitank', selected_articles=selected_articles,                dt_prev_year=dt_prev_year, dt_prev_month=dt_prev_month.zfill(2), dt_next_year=dt_next_year, dt_next_month=dt_next_month.zfill(2))


@ app.route('/<date>')  # /<date>とすると/の場合にもfavicon.icoで実行されてしまうためcreated-atを挟んでいる
def other(date):
    if date == 'favicon.ico':
        return index()
    else:
        with open('access_token.json') as f:
            df = json.load(f)

        access_token = df['access_token']
        headers = {'Authorization': 'Bearer '+access_token}

        selected_articles = []

        target_year = date[:4]  # '2021'
        target_month = date[4:]  # '03'
        dt_now = datetime.date(int(target_year), int(target_month), 1)
        dt_prev_year = str((dt_now - relativedelta(months=1)).year)
        dt_prev_month = str((dt_now - relativedelta(months=1)).month)
        dt_next_year = str((dt_now + relativedelta(months=1)).year)
        dt_next_month = str((dt_now + relativedelta(months=1)).month)

        _, lastday = calendar.monthrange(int(target_year), int(target_month))
        for page in range(1, 2):
            url = 'https://qiita.com/api/v2/items?page='+str(page)+'&per_page=100&query=created%3A%3E'+target_year+'-'+target_month+'-01+created%3A%3C'+target_year+'-' + \
                target_month+'-'+str(lastday)+'+stocks%3A%3E30'

            response = requests.get(url, headers=headers)
            selected_articles.append(json.loads(response.text))

        return render_template('index.html', title='Qiitank', selected_articles=selected_articles, dt_prev_year=dt_prev_year, dt_prev_month=dt_prev_month.zfill(2), dt_next_year=dt_next_year, dt_next_month=dt_next_month.zfill(2))


if __name__ == "__main__":
    app.run(debug=True, port=8888, threaded=True)

# 実行方法
# python qiita_legend.py
