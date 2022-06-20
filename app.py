import calendar
import datetime
import json
import os

import jinja2  # import Environment, FileSystemLoader, select_autoescape
import requests
from chalice import Chalice, Response
from dateutil.relativedelta import relativedelta

from chalicelib import API_KEY

app = Chalice(app_name='qiitank')


@app.route('/', methods=["GET"], content_types=["*/*"])
def index():
    access_token = API_KEY
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
    for page in range(1, 2):
        url = 'https://qiita.com/api/v2/items?page='+str(page)+'&per_page=100&query=created%3A%3E'+target_year+'-'+target_month.zfill(2)+'-01+created%3A%3C'+target_year+'-' + \
            target_month.zfill(2)+'-'+str(lastday)+'+stocks%3A%3E300'

        response = requests.get(url, headers=headers)
        selected_articles.append(json.loads(response.text))
    selected_articles_formatted = []
    selected_articles_sorted = []
    for articles in selected_articles:
        for article in articles:
            item = {"likes_count": article["likes_count"], "title": article["title"], "created_at": article["created_at"], "updated_at": article["updated_at"]}
            item["created_at"] = datetime.datetime.strptime(item["created_at"], '%Y-%m-%dT%H:%M:%S%z').strftime('%Y-%m-%d')
            item["updated_at"] = datetime.datetime.strptime(item["updated_at"], '%Y-%m-%dT%H:%M:%S%z').strftime('%Y-%m-%d')
            selected_articles_formatted.append(item)
            selected_articles_sorted = sorted(selected_articles_formatted, key=lambda x: x["likes_count"], reverse=True)
    context = {"selected_articles": selected_articles_sorted,                "dt_prev_year": dt_prev_year,
               "dt_prev_month": dt_prev_month.zfill(2), "dt_next_year": dt_next_year, "dt_next_month": dt_next_month.zfill(2)}
    template = render("chalicelib/templates/index.html", context)
    return Response(template, status_code=200, headers={"Content-Type": "text/html;charset=UTF-8", "Access-Control-Allow-Origin": "*"})


@app.route('/{date}', methods=["GET"], content_types=["*/*"])  # /<date>とすると/の場合にもfavicon.icoで実行されてしまうためcreated-atを挟んでいる
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
                target_month+'-'+str(lastday)+'+stocks%3A%3E300'

            response = requests.get(url, headers=headers)
            selected_articles.append(json.loads(response.text))
        selected_articles_formatted = []
        selected_articles_sorted = []
        for articles in selected_articles:
            for article in articles:
                item = {"likes_count": article["likes_count"], "title": article["title"], "created_at": article["created_at"], "updated_at": article["updated_at"]}
                selected_articles_formatted.append(item)
                selected_articles_sorted = sorted(selected_articles_formatted, key=lambda x: x["likes_count"], reverse=True)

        context = {"selected_articles": selected_articles_sorted,                "dt_prev_year": dt_prev_year,
                   "dt_prev_month": dt_prev_month.zfill(2), "dt_next_year": dt_next_year, "dt_next_month": dt_next_month.zfill(2)}
        template = render("chalicelib/templates/index.html", context)
        return Response(template, status_code=200, headers={"Content-Type": "text/html; charset=UTF-8", "Access-Control-Allow-Origin": "*"})


def render(tpl_path, context):
    path, filename = os.path.split(tpl_path)
    return jinja2.Environment(loader=jinja2.FileSystemLoader(path or "./")).get_template(filename).render(context)


@app.route('/chalicelib/static/css/style.css')
def cssindex():
    with open('chalicelib/static/css/style.css') as f:
        data = f.read()
    return Response(body=data, status_code=200, headers={"Content-Type": "text/css", "Access-Control-Allow-Origin": "*"})


@app.route('/chalicelib/favicon.ico')
def faviconindex():
    with open('chalicelib/static/favicon.ico', 'rb') as fp:
        data = fp.read()
    return Response(body=data, status_code=200, headers={"Content-Type": "image/png", "Access-Control-Allow-Origin": "*"})


if __name__ == "__main__":
    app.run(debug=True, port=8888, threaded=True)

# 実行方法
# chalice local
