import requests
import json


class HTTPClient:

    urls = {
        'reddit': 'https://www.reddit.com/r/news/top.json?limit=10',
        'news': 'http://newsapi.org/v2/top-headlines?category=general&pageSize=10&page=1&' + 'apiKey=',
    }

    @staticmethod
    def post(url: str, data: dict={}, auth=True):    
        pass
    
    @staticmethod
    def get(url: str, data: dict={}, auth=False):    
        return requests.get(HTTPClient.urls.get(url, None), data=data, headers=HTTPClient.get_headers(auth)).json()
    
    @staticmethod
    def get_headers(auth: bool):
        if auth is True:
            headers={'Content-Type': 'application/json', 'Authorization': 'Bearer '+HTTPClient.secret}
        else:
            headers={'User-agent': 'your bot 0.1'}
        return headers
