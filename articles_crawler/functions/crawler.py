import calendar
import datetime
import json
import os
import uuid

import requests
from aws_xray_sdk.core import patch_all
from common.log import Log
from dateutil.relativedelta import relativedelta
from db_access import DBAccessor

log = Log(__name__)
logger = log.setup_logger()
patch_all()

MAX_PAGE_SIZE = 100
MONTH_NUM = 12
PAGE_NUM = 1
PER_PAGE = 100
STOCKS = 100  # 検索対象にするstock数
URL_QIITA_API_V2 = os.environ["URL_QIITA_API_V2"]


class Crawler:
    """Crawl articles from Qiita API"""
    access_token = os.environ['API_KEY']
    headers = {'Authorization': 'Bearer '+access_token}

    def __init__(self):
        self.__target_list = self.__create_target_date()
        self.__db_accessor = DBAccessor()

    def __get_stocks(self, article_id: str):
        """Get an article's stocker count"""
        stock_counter = 0
        for i in range(1, MAX_PAGE_SIZE+1):
            url = URL_QIITA_API_V2 + '/items/'+article_id + '/stockers?page='+str(i)+'&per_page='+str(PER_PAGE)

            response = requests.get(url, headers=Crawler.headers)
            try:
                res_content = json.loads(response.text)
            except Exception as e:
                logger.error("error = %s", e)
                logger.error("stock counter is suspended. counter: ", stock_counter)
                return stock_counter
            if len(res_content) == 0:
                return stock_counter

            stock_counter += len(res_content)
        return stock_counter

    def __create_items(self, item: dict[str, str], target_pk: str):
        """Create an article item"""
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

    def __save_articles(self, items: list[dict[str, str]], target: dict[str, str]):
        """Save articles"""
        target_pk = target.get('target_each_pk')
        for item in items:

            try:
                article = self.__create_items(item, target_pk)
                self.__db_accessor.put_item(article)
            except Exception as e:
                logger.error("error = %s", e)
                logger.error("save articles was failed.")
                return 500

        return 200

    def __get_articles(self, target: dict[str, str]):
        """Get articles"""
        target_year = target.get('target_each_year')
        target_month = target.get('target_each_month')
        # 対象月をキーとして検索結果データを入れ替える
        _, lastday = calendar.monthrange(int(target_year), int(target_month))
        selected_articles = []
        for page in range(1, 1+PAGE_NUM):  # FIXME クエリ結果が100件以上あると2ページ目となるため修正が必要(まだ余裕があるためそのままにしている)
            url = URL_QIITA_API_V2 + '/items?page='+str(page)+'&per_page=100&query=created%3A%3E'+target_year+'-'+target_month+'-01+created%3A%3C'+target_year+'-' + \
                target_month+'-'+str(lastday)+'+stocks%3A%3E' + str(STOCKS)

            response = requests.get(url, headers=Crawler.headers)
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
        """Clear articles form DB

        Args:
            target (list[dict[str, str]]): _description_

        Returns:
            _type_: _description_
        """
        return self.__db_accessor.delete_items(target.get('target_each_pk'))

    def __create_target_date(self):
        """Create month number list"""
        dt_now = datetime.datetime.now()
        target_list = []
        for i in range(MONTH_NUM):
            target_each_year = (dt_now - relativedelta(months=i)).strftime('%Y')  # '2022'
            target_each_month = (dt_now - relativedelta(months=i)).strftime('%m')  # '06'
            target_each_pk = target_each_year + '-' + target_each_month
            target_list.append({'target_each_year': target_each_year, 'target_each_month': target_each_month, 'target_each_pk': target_each_pk})
        return target_list

    def calc_target_month_index(self):
        """Decide proccessed month number"""
        dt_now = datetime.datetime.now()
        dt_now_hour = dt_now.strftime('%H')
        target_month_index = (int(dt_now_hour) % 12)
        return target_month_index

    def run(self):
        """Main

        Returns:
            int: _description_
        """
        # 現在時刻から処理する月を１つ決定
        target_month_index = self.calc_target_month_index()
        target = self.__target_list[target_month_index]
        logger.info("*** %s - %s", target.get("target_each_year"),  target.get("target_each_month"))
        self.__delete_articles(target)
        result = self.__get_articles(target)
        self.__save_articles(result, target)
