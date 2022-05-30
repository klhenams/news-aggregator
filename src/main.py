from typing import Union

from fastapi import FastAPI

from app.services.news.news_crud import NewsCrudFactory
from app.wrappers.news import Reddit

app = FastAPI()
newscrud_service = NewsCrudFactory.default()

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.get("/news/")
def read_item():
    return newscrud_service.list()


@app.post("/news/reddit")
def read_item():
    return Reddit.get()
