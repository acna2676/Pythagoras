import calendar
import datetime
import json
import os
import uuid
from concurrent.futures import ThreadPoolExecutor

import requests
from dateutil.relativedelta import relativedelta

from db_access import DBAccessor

DEBUG = True
if DEBUG:  # FIXME APIKEYがDEBUGの時しか読み込まれない, 本場では不要なため外出しする
    from dotenv import load_dotenv
    load_dotenv(verbose=True)

MAX_PAGE_SIZE = 100
MONTH_NUM = 12
PAGE_NUM = 1
PER_PAGE = 100
STOCKS = 300  # 検索対象にするstock数
URL_QIITA_API_V2 = 'https://qiita.com/api/v2'


class Crowler:
    # NOTE ファクトリにできそう
    access_token = os.environ['API_KEY']
    headers = {'Authorization': 'Bearer '+access_token}

    def __init__(self):
        self.__target_list = self.__create_target_date()
        self.__db_accessor = DBAccessor()

    def __get_stocks(self, article_id: str):
        stock_counter = 0
        for i in range(1, MAX_PAGE_SIZE+1):
            if DEBUG:
                import time
                url = 'http://localhost:5000/api/user_stocks'
                time.sleep(1)  # 1秒待ってreturn
                return stock_counter
            else:
                url = URL_QIITA_API_V2 + '/items/'+article_id + '/stockers?page='+str(i)+'&per_page='+PER_PAGE

            response = requests.get(url, headers=Crowler.headers)
            try:
                res_content = json.loads(response.text)
            except Exception as e:
                print("error = ", e)
                import sys
                sys.exit()
            if len(res_content) == 0:
                return stock_counter

            stock_counter += len(res_content)

    def __create_items(self, item, target_pk):
        article_id = item.get('article_id')
        article_id_sk = str(uuid.uuid4())
        title = item.get('title')
        url = item.get('url')
        likes_count = item.get('likes_count')
        stocks = self.__get_stocks(article_id)
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
        return items

    def __save_articles(self, items: list[dict[str, str]], target):

        target_pk = target.get('target_each_pk')
        for item in items:

            try:
                article = self.__create_items(item, target_pk)
                self.__db_accessor.put_item(article)
            except Exception as e:
                print(e)
                return 500

        return 200

    def __get_articles(self, target):
        target_year = target.get('target_each_year')
        target_month = target.get('target_each_month')
        # 対象月をキーとして検索結果データを入れ替える
        _, lastday = calendar.monthrange(int(target_year), int(target_month))
        selected_articles = []
        for page in range(1, 1+PAGE_NUM):  # FIXME クエリ結果が100件以上あると2ページ目となるため修正が必要(まだ余裕があるためそのままにしている)
            if DEBUG == True:
                url = 'http://localhost:5000/api/article'
            else:
                url = URL_QIITA_API_V2 + '/items?page='+str(page)+'&per_page=100&query=created%3A%3E'+target_year+'-'+target_month+'-01+created%3A%3C'+target_year+'-' + \
                    target_month+'-'+str(lastday)+'+stocks%3A%3E' + STOCKS

            response = requests.get(url, headers=Crowler.headers)
            selected_articles.append(json.loads(response.text))
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

    def __delete_articles(self, target: list[dict[str, str]]):
        """DBに保存されている記事を全て削除する

        Args:
            target (list[dict[str, str]]): _description_

        Returns:
            _type_: _description_
        """
        return self.__db_accessor.delete_items(target.get('target_each_pk'))

    def __create_target_date(self):
        dt_now = datetime.datetime.now()
        target_list = []
        for i in range(MONTH_NUM):
            target_each_year = (dt_now - relativedelta(months=i)).strftime('%Y')  # '2022'
            target_each_month = (dt_now - relativedelta(months=i)).strftime('%m')  # '06'
            target_each_pk = target_each_year + '-' + target_each_month
            target_list.append({'target_each_year': target_each_year, 'target_each_month': target_each_month, 'target_each_pk': target_each_pk})
        return target_list

    def run(self):
        """Qiita API v2からの記事取得、保存をマルチスレッドで実行

        Returns:
            int: _description_
        """
        # FIXME 503 if max_worler > 1
        with ThreadPoolExecutor(max_workers=3) as executor:
            for target in self.__target_list:
                print("***", target.get("target_each_year"), "-", target.get("target_each_month"))
                # if DEBUG == False:
                self.__delete_articles(target)
                result = self.__get_articles(target)
                executor.submit(self.__save_articles, result, target)
                # self.put_items(result, target)
        return 200
