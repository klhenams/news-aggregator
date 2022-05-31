from abc import ABC, abstractmethod
from typing import List

from ..services.news.news_crud import NewsCrudFactory
from ..models.news import News
from ..utils.http_client import HTTPClient




class NewsWrapper(ABC):

    @abstractmethod
    def get(self) -> News:
        """ fetch news articles """

    @abstractmethod
    def parse_response(self, results) -> List[News]:
        """ convert json to data structure """
    

class Reddit(NewsWrapper):

    in_memory_news = NewsCrudFactory.default()
    r = HTTPClient()

    @staticmethod
    def get():
        return Reddit.parse_response(Reddit.r.get('reddit'))
           

    @staticmethod
    def parse_response(results) -> List[News]:
        for article in results["data"]["children"]:
            Reddit.in_memory_news.create(
                headline=article["data"]["title"],
                link=article["data"]["url"],
                source="reddit")
        return Reddit.in_memory_news.list()
    

class NewsSource(NewsWrapper):

    in_memory_news = NewsCrudFactory.default()
    r = HTTPClient()

    @staticmethod
    def get():
        return NewsSource.parse_response(NewsSource.r.get('news'))
           

    @staticmethod
    def parse_response(results) -> List[News]:
        for article in results["articles"]:
            NewsSource.in_memory_news.create(
                headline=article["title"],
                link=article["url"],
                source="newsapi")
        return NewsSource.in_memory_news.list()