import unittest

from ..models.news import News
from ..services.news.news_crud import NewsCrudFactory


class MyTestCase(unittest.TestCase):
    crud_service = NewsCrudFactory.default()

    def test_create_news(self):
        news = self.crud_service.create(headline='my headline text', link='https://example.com', source="reddit")
        self.assertIsInstance(news, News)

    def test_list_news(self):
        articles = self.crud_service.list()
        self.assertIsInstance(articles, list)
    
    def test_search_news(self):
        articles = self.crud_service.search()
        self.assertIsInstance(articles, list)


if __name__ == '__main__':
    unittest.main()
