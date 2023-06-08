from flask import json, request, Flask
from werkzeug.exceptions import HTTPException

from schemas import (
    GetArticleTopDayRequest,
    GetMostViewedArticlesRequest,
    GetTotalArticleViewsRequest
)


V1_BASE_URL="/api/v1"

app = Flask(__name__)


@app.errorhandler(HTTPException)
def handle_exception(e):
    """Return JSON instead of HTML for HTTP errors."""
    # start with the correct headers and status code from the error
    response = e.get_response()
    # replace the body with JSON
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })
    response.content_type = "application/json"
    return response


@app.get(f"{V1_BASE_URL}/articles/top")
def most_viewed_articles():
    """
    Retrieve a list of the most viewed articles for a given week or
    month.
    """
    request_schema = GetMostViewedArticlesRequest(
        day=request.args.get("day"),
        month=request.args.get("month"),
        year=request.args.get("year"),
        time_period=request.args.get("time_period"),
    )

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
    request_schema = GetTotalArticleViewsRequest(
        day=request.args.get("day"),
        month=request.args.get("month"),
        year=request.args.get("year"),
        time_period=request.args.get("time_period"),
        title=request.args.get("title"),
    )

    return {
      "title": request_schema.title,
      "start_date": "DDMMYYYY",
      "end_date": "DDMMYYYY",
      "total_views": 12345
    }


@app.get(f"{V1_BASE_URL}/articles/top_day")
def article_top_day():
    """
    For an article in a given month, return which day it got the most
    views.
    """
    request_schema = GetArticleTopDayRequest(
        month=request.args.get("month"),
        year=request.args.get("year"),
        title=request.args.get("title"),
    )

    return {
      "title": request_schema.title,
      "date": "DDMMYYYY",
      "views": 12345
    }
