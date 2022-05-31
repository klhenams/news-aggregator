# News Aggregator

A simple news aggregation application

Requirements
---

* Python `3.9+`
* fastapi `0.68+`



> ***Note***: Use a virtual environment or container for project isolation 

## 1. Clone project

 `git clone https://github.com/maaddae/news-aggregator.git`

## 2. Create virtual environment

Step into the root of the application to create and activate the environment

`python3 -m venv env`

To activate run the below command

`source env/bin/activate`

## 3. Install dependencies
Still at the root directory, run this pip command to install dependencies

`pip install -r requirements.txt`

## 3. Running application

Run command to start application

`uvicorn main:app --reload`
