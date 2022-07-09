import calendar
import datetime
import json
import os
import uuid
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

import boto3
import requests
from boto3.dynamodb.conditions import Key
from dateutil.relativedelta import relativedelta


def get_database():
    endpoint = os.environ.get('DB_ENDPOINT')
    if endpoint:
        return boto3.resource('dynamodb', endpoint_url=endpoint)
    else:
        return boto3.resource('dynamodb')


class Crowler:
    DEBUG = False
    # NOTE ファクトリにできそう
    dynamodb = get_database()
    TABLE_NAME = os.environ.get('DB_TABLE_NAME')
    table = dynamodb.Table(TABLE_NAME)

    access_token = '38b71e80eb38b29f4c9dfe728b2817121754038c'  # os.environ['API_KEY']
    headers = {'Authorization': 'Bearer '+access_token}

    def __init__(self):
        # self.__selected_articles = []
        self.__dt_now = datetime.datetime.now()
        self.__target_list = []

        for i in range(12):
            target_each_year = (self.__dt_now - relativedelta(months=i)).strftime('%Y')  # '2022'
            target_each_month = (self.__dt_now - relativedelta(months=i)).strftime('%m')  # '06'
            target_each_pk = target_each_year + '-' + target_each_month
            self.__target_list.append({'target_each_year': target_each_year, 'target_each_month': target_each_month, 'target_each_pk': target_each_pk})

        self.__target_year = self.__dt_now.strftime('%y')  # str(self.__dt_now.year)  # '2021'
        self.__target_month = self.__dt_now.strftime('%m')  # str(self.__dt_now.month)  # '3'
        self.__pk = self.__target_year + '-' + self.__target_month

    def __get_stocks(self, article_id):
        stock_counter = 0
        for i in range(1, 101):
            if self.DEBUG == True:
                import time
                url = 'http://localhost:5000/api/user_stocks'
                time.sleep(1)  # 1秒待ってreturn
                return stock_counter
            else:
                url = 'https://qiita.com/api/v2/items/'+article_id + '/stockers?page='+str(i)+'&per_page=100'

            response = requests.get(url, headers=Crowler.headers)
            # print("response = ", response.text)
            try:
                res_content = json.loads(response.text)
            except Exception as e:
                # print("response.text = ", response.text)
                print("urlll = ", url)
                print("response.status_code = ", response.status_code)
                print("error = ", e)
                import sys
                sys.exit()
            if len(res_content) == 0:
                return stock_counter

            stock_counter += len(res_content)

    def put_items(self, items, target):

        target_pk = target.get('target_each_pk')
        for item in items:
            article_id = item.get('article_id')
            article_id_sk = str(uuid.uuid4())
            title = item.get('title')
            url = item.get('url')
            likes_count = item.get('likes_count')
            stocks = self.__get_stocks(article_id)  # FIXME 現状は取得できない?
            created_at = item.get('created_at')
            updated_at = item.get('updated_at')

            items = {
                "pk": target_pk,
                "sk": 'id_' + article_id_sk,
                "title": title,
                "url": url,
                "likes_count": likes_count,
                "stocks": stocks,
                "created_at": created_at,
                "updated_at": updated_at
            }

            try:
                Crowler.table.put_item(
                    Item=items
                )
            except Exception as e:
                print(e)
                return 500

        return 200

    def delete_items(self, target):
        pk = target.get('target_each_pk')
        delete_targets = Crowler.table.query(
            KeyConditionExpression=Key('pk').eq(pk) & Key('sk').begins_with("id_")
        )['Items']
        # print('delete_targets = ', delete_targets)

        for target in delete_targets:
            keys = {
                "pk": target.get('pk'),
                "sk": target.get('sk'),
            }

            try:
                Crowler.table.delete_item(
                    Key=keys
                )
            except Exception as e:
                print(e)
                return 500

        return 200

    def get_ranking(self, target):
        target_year = target.get('target_each_year')
        target_month = target.get('target_each_month')
        # 対象月をキーとして検索結果データを入れ替える
        _, lastday = calendar.monthrange(int(target_year), int(target_month))
        selected_articles = []
        for page in range(1, 2):  # NOTE クエリ結果が100件以上あると2ページ目となるため修正が必要(まだ余裕があるためそのままにしている)
            if self.DEBUG == True:
                url = 'http://localhost:5000/api/article'
            else:
                url = 'https://qiita.com/api/v2/items?page='+str(page)+'&per_page=100&query=created%3A%3E'+target_year+'-'+target_month+'-01+created%3A%3C'+target_year+'-' + \
                    target_month+'-'+str(lastday)+'+stocks%3A%3E300'

            response = requests.get(url, headers=Crowler.headers)
            selected_articles.append(json.loads(response.text))
            # print("selected_articles = ", selected_articles)
            # return
        # print("selected_articles = ", selected_articles)
        selected_articles_formatted = []
        selected_articles_sorted = []
        for articles in selected_articles:
            for article in articles:
                item = {"article_id": article["id"], "likes_count": article["likes_count"], "title": article["title"],
                        "url": article["url"], "created_at": article["created_at"], "updated_at": article["updated_at"]}
                item["created_at"] = datetime.datetime.strptime(item["created_at"], '%Y-%m-%dT%H:%M:%S%z').strftime('%Y-%m-%d')
                item["updated_at"] = datetime.datetime.strptime(item["updated_at"], '%Y-%m-%dT%H:%M:%S%z').strftime('%Y-%m-%d')
                selected_articles_formatted.append(item)
        selected_articles_sorted = sorted(selected_articles_formatted, key=lambda x: x["likes_count"], reverse=True)
        return selected_articles_sorted

    def create(self):
        # FIXME 503 if max_worler > 1
        with ThreadPoolExecutor(max_workers=1) as executor:
            for target in self.__target_list:
                print("***", target.get("target_each_year"), "-", target.get("target_each_month"))
                if self.DEBUG == False:
                    self.delete_items(target)
                result = self.get_ranking(target)

                executor.submit(self.put_items, result, target)
                # self.put_items(result, target)
        return 200


def lambda_main():

    crowler = Crowler()
    # with ProcessPoolExecutor(max_workers=6) as executor:
    # with ThreadPoolExecutor(max_workers=3) as executor:
    # executor.submit(crowler.create)
    status_code = crowler.create()

    return status_code


def lambda_handler(_, __):
    status_code = 200
    message = 'Success'

    status_code = lambda_main()

    body = {
        'message': message,
    }

    return {'statusCode': status_code,
            'body': json.dumps(body),
            'headers': {'Content-Type': 'application/json'}}


if __name__ == '__main__':
    lambda_handler(None, None)
