import calendar
import datetime
import json
import os

import boto3
import jinja2  # import Environment, FileSystemLoader, select_autoescape
from boto3.dynamodb.conditions import Key
from chalice import Chalice, Response
from dateutil.relativedelta import relativedelta

from chalicelib import API_KEY

app = Chalice(app_name='qiitank')


def get_database():
    endpoint = os.environ.get('DB_ENDPOINT')
    if endpoint:
        return boto3.resource('dynamodb', endpoint_url=endpoint)
    else:
        return boto3.resource('dynamodb')


class DBAccessor:

    # NOTE ファクトリにできそう
    dynamodb = get_database()
    TABLE_NAME = os.environ.get('DB_TABLE_NAME')
    table = dynamodb.Table(TABLE_NAME)

    def __init__(self, pk):
        self.__pk = pk

    def get_items(self):

        try:
            response = DBAccessor.table.query(
                KeyConditionExpression=Key('pk').eq(self.__pk) & Key('sk').begins_with("id_")
            )
        except Exception as e:
            print("e = ", e)
            return 500

        items = response['Items']  # [0]

        return items


@app.route('/', methods=["GET"], content_types=["*/*"])
def index():
    stocks_fileter = 0
    query_params = app.current_request.query_params
    if query_params:
        stocks_fileter = int(query_params.get('stocks'))
    print("query = ", query_params)

    access_token = API_KEY
    headers = {'Authorization': 'Bearer '+access_token}

    selected_articles = []

    dt_now = datetime.datetime.now()
    dt_prev_year = str((dt_now - relativedelta(months=1)).year)
    dt_prev_month = str((dt_now - relativedelta(months=1)).month)
    dt_next_year = str((dt_now + relativedelta(months=1)).year)
    dt_next_month = str((dt_now + relativedelta(months=1)).month)

    target_year = str(dt_now.year)  # '2021'
    target_month = str(dt_now.month).zfill(2)  # '03'

    pk = target_year + '-' + target_month

    db_accessor = DBAccessor(pk)
    selected_articles_sorted = db_accessor.get_items()
    # stock数がquery_params以上のものでフィルタリング
    print("selected_articles_sorted = ", selected_articles_sorted)
    selected_articles_sorted = filter(lambda x: x["stocks"] >= stocks_fileter, selected_articles_sorted)

    context = {"selected_articles": selected_articles_sorted, "dt_prev_year": dt_prev_year,
               "dt_prev_month": dt_prev_month.zfill(2), "dt_next_year": dt_next_year, "dt_next_month": dt_next_month.zfill(2)}
    template = render("chalicelib/templates/index.html", context)
    return Response(template, status_code=200, headers={"Content-Type": "text/html;charset=UTF-8", "Access-Control-Allow-Origin": "*"})


@app.route('/{date}', methods=["GET"], content_types=["*/*"])  # /<date>とすると/の場合にもfavicon.icoで実行されてしまうためcreated-atを挟んでいる
def other(date):
    if date == 'favicon.ico':
        # return index()
        return
    else:
        stocks_fileter = 0
        query_params = app.current_request.query_params
        if query_params:
            stocks_fileter = int(query_params.get('stocks'))
        print("query = ", query_params)

        access_token = API_KEY
        headers = {'Authorization': 'Bearer '+access_token}

        selected_articles = []
        target_year = date[:4]  # '2021'
        target_month = date[4:]  # '03'
        dt_now = datetime.date(int(target_year), int(target_month), 1)
        dt_prev_year = str((dt_now - relativedelta(months=1)).year)
        dt_prev_month = str((dt_now - relativedelta(months=1)).month)
        dt_next_year = str((dt_now + relativedelta(months=1)).year)
        dt_next_month = str((dt_now + relativedelta(months=1)).month)

        pk = target_year + '-' + target_month
        db_accessor = DBAccessor(pk)
        selected_articles_sorted = db_accessor.get_items()
        selected_articles_sorted = filter(lambda x: x["stocks"] >= stocks_fileter, selected_articles_sorted)

        context = {"selected_articles": selected_articles_sorted, "dt_prev_year": dt_prev_year,
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
