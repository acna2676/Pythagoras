import os

import pytest

from ..functions.crawler import Crawler


# @pytest.mark.usefixtures("read_event")
class TestReadS3Event:
    def test_bucket(self):
        crawler = Crawler()
        result = crawler._Crawler.__get_stocks("article_id")
        assert result == 0
