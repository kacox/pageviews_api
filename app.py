from flask import request, Flask


V1_BASE_URL="/api/v1"

app = Flask(__name__)


@app.get(f"{V1_BASE_URL}/articles/top")
def most_viewed_articles():
    """
    Retrieve a list of the most viewed articles for a given week or
    month.
    """
    # TODO: how to only accept {week|month} for time_period
    time_period = request.args.get("time_period")
    day = request.args.get("day")
    month = request.args.get("month")
    year = request.args.get("year")

    return {
      "count": 2,
      "start_date": "DDMMYYYY",
      "end_date": "DDMMYYYY",
      "articles": [
        {
          "title": "Article Title",
          "total_views": 12345
        },
        {
          "title": "Another Article Title",
          "total_views": 11857
        },
      ]
    }


@app.get(f"{V1_BASE_URL}/articles/total_views")
def total_article_views():
    """
    For an article, get the total views for that article in a given a
    week or a month.
    """
    title = request.args.get("title")
    time_period = request.args.get("time_period")
    day = request.args.get("day")
    month = request.args.get("month")
    year = request.args.get("year")

    return {
      "title": title,
      "start_date": "DDMMYYYY",
      "end_date": "DDMMYYYY",
      "total_views": 12345
    }


@app.get(f"{V1_BASE_URL}/articles/top_day")
def top_day():
    """
    For an article in a given month, return which day it got the most
    views.
    """
    title = request.args.get("title")
    month = request.args.get("month")
    year = request.args.get("year")

    return {
      "title": title,
      "date": "DDMMYYYY",
      "views": 12345
    }
