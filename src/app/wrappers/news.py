from abc import ABC, abstractmethod
from typing import List
import requests

from ..services.news.news_crud import NewsCrudFactory
from ..models.news import News




class NewsWrapper(ABC):

    @abstractmethod
    def get(self) -> News:
        """ fetch news articles """

    @abstractmethod
    def parse_response(self, results) -> List[News]:
        """ convert json to data structure """
    

class Reddit(NewsWrapper):

    in_memory_news = NewsCrudFactory.default()

    @staticmethod
    def get():
        results = requests.get(
            'https://www.reddit.com/r/news/top.json?limit=10', 
            headers={'User-agent': 'your bot 0.1'}).json()
        return Reddit.parse_response(results)
           

    @staticmethod
    def parse_response(results) -> List[News]:
        for article in results["data"]["children"]:
            Reddit.in_memory_news.create(
                headline=article["data"]["title"],
                link=article["data"]["url"],
                source="reddit")
        return Reddit.in_memory_news.list()
