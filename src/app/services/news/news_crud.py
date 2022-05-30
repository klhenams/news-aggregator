from abc import ABC, abstractmethod
from typing import List

from ...models.news import News


class NewsCrud(ABC):
    """ CRUD stub for messaging """

    @abstractmethod
    def create(self, headline: str, link: str, source: str) -> News:
        """ Create a message """

    @abstractmethod
    def list(self) -> List[News]:
        """ Fetch all messages """
    
    @abstractmethod
    def search(self, query: str) -> News:
        """ Create a message """


class InMemoryMessageCrud(NewsCrud):
    """ Manage articles in memory. Articles will be lost when the application restarts """

    articles: List[News] = []

    def create(self, headline: str, link: str, source: str) -> News:
        new_article = News(headline, link, source)
        self.articles.append(new_article)
        return new_article

    def list(self) -> List[News]:
        return self.articles
    
    
    def search(self, query: str) -> News:
        pass



class NewsCrudFactory:
    """ Generator for Message CRUD Services """

    @staticmethod
    def default() -> NewsCrud:
        return InMemoryMessageCrud()
