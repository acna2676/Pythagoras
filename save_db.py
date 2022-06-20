import calendar
import datetime
import json
import uuid

import boto3
import requests
from boto3.dynamodb.conditions import Key

# from dateutil.relativedelta import relativedelta


class Crowler:
    # from chalicelib import API_KEY
    # FIXME ファクトリにできそう
    # dynamodb = boto3.resource('dynamodb')
    dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000')
    table = dynamodb.Table('qiitank')

    # FIXME __access_token = API_KEY
    access_token = '38b71e80eb38b29f4c9dfe728b2817121754038c'
    headers = {'Authorization': 'Bearer '+access_token}

    def __init__(self):
        self.__selected_articles = []
        self.__dt_now = datetime.datetime.now()
        # dt_prev_year = str((dt_now - relativedelta(months=1)).year)
        # dt_prev_month = str((dt_now - relativedelta(months=1)).month)
        # dt_next_year = str((dt_now + relativedelta(months=1)).year)
        # dt_next_month = str((dt_now + relativedelta(months=1)).month)

        self.__target_year = str(self.__dt_now.year)  # '2021'
        self.__target_month = str(self.__dt_now.month)  # '3'
        self.__pk = self.__target_year + '-' + self.__target_month

    def put_items(self, items):

        for item in items:
            article_id = str(uuid.uuid4())
            title = item.get('title')
            url = item.get('url')
            likes_count = item.get('likes_count')
            created_at = item.get('created_at')
            updated_at = item.get('updated_at')

            items = {
                "pk": self.__pk,
                "sk": 'id_' + article_id,
                "title": title,
                "url": url,
                "likes_count": likes_count,
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

    def delete_items(self):
        delete_targets = Crowler.table.query(
            KeyConditionExpression=Key('pk').eq(self.__pk) & Key('sk').begins_with("id_")
        )['Items']
        print('delete_targets = ', delete_targets)

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

    def get_ranking(self):
        # 対象月をキーとして検索結果データを入れ替える

        _, lastday = calendar.monthrange(int(self.__target_year), int(self.__target_month))
        for page in range(1, 2):
            url = 'https://qiita.com/api/v2/items?page='+str(page)+'&per_page=100&query=created%3A%3E'+self.__target_year+'-'+self.__target_month+'-01+created%3A%3C'+self.__target_year+'-' + \
                self.__target_month+'-'+str(lastday)+'+stocks%3A%3E300'

            response = requests.get(url, headers=Crowler.headers)
            self.__selected_articles.append(json.loads(response.text))
        selected_articles_formatted = []
        selected_articles_sorted = []
        for articles in self.__selected_articles:
            for article in articles:
                item = {"likes_count": article["likes_count"], "title": article["title"], "url": article['url'], "created_at": article["created_at"], "updated_at": article["updated_at"]}
                item["created_at"] = datetime.datetime.strptime(item["created_at"], '%Y-%m-%dT%H:%M:%S%z').strftime('%Y-%m-%d')
                item["updated_at"] = datetime.datetime.strptime(item["updated_at"], '%Y-%m-%dT%H:%M:%S%z').strftime('%Y-%m-%d')
                selected_articles_formatted.append(item)
                selected_articles_sorted = sorted(selected_articles_formatted, key=lambda x: x["likes_count"], reverse=True)
        print('selected_articles_sorted = ', selected_articles_sorted)
        return selected_articles_sorted


def lambda_main():

    crowler = Crowler()
    status_code = crowler.delete_items()
    result = crowler.get_ranking()
    status_code = crowler.put_items(result)

    return status_code


def handler(_, __):
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
    handler(None, None)
