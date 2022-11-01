import os
import sys

import pytest
from functions.crawler import Crawler

# sys.path.append('../functions')

# @pytest.mark.usefixtures("read_event")


class TestReadS3Event:
    def test_bucket(self):
        crawler = Crawler()
        # result = crawler._Crawler.__get_stocks("article_id")
        # assert result == 0
        assert 0 == 0
