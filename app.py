from calendar import monthrange
from datetime import date, timedelta

from flask import json, request, Flask
from werkzeug.exceptions import BadRequest, HTTPException
import requests

from schemas import (
    GetArticleTopDayRequest,
    GetMostViewedArticlesRequest,
    GetTotalArticleViewsRequest
)


USER_AGENT_HEADER = {'User-Agent': 'pageviewsAPI/0.0 (ka.cox@outlook.com)'}
V1_BASE_URL="/api/v1"
WIKIMEDIA_BASE_URL = "https://wikimedia.org/api/rest_v1"
WIKIMEDIA_ACCESS_PARAM = "all-access"
WIKIMEDIA_PROJECT_PARAM = "en.wikipedia"

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

    if request_schema.time_period == "week":
        start_date = date(
            request_schema.year, request_schema.month, request_schema.day
        )
        days = [start_date + timedelta(days=x) for x in range(7)]
    elif request_schema.time_period == "month":
        start_date = date(request_schema.year, request_schema.month, 1)
        days = [
            start_date + timedelta(days=days_offset)
            for days_offset in range(
                monthrange(
                    request_schema.year, request_schema.month
                )[1]
            )
        ]
    else:
        raise BadRequest("time_period must be 'month' or 'week'")

    article_counts = {}
    for day in days:
        resp = requests.get(
            f"{WIKIMEDIA_BASE_URL}/metrics/pageviews/top/"
            + f"{WIKIMEDIA_PROJECT_PARAM}/{WIKIMEDIA_ACCESS_PARAM}/"
            + f"{request_schema.year}/{request_schema.month}/"
            + f"{request_schema.day}",
            headers=USER_AGENT_HEADER,
        )
        resp.raise_for_status()

        articles = resp.json()["items"][0]["articles"]
        for article in articles:
            article_counts[article["article"]] = article_counts.get(
                article["article"], 0
            ) + article["views"]
    final_articles = [
        {"title": title, "total_views": views}
        for title, views in article_counts.items()
    ]

    return {
      "count": len(article_counts),
      "start_date": start_date.isoformat(),
      "end_date": days[-1].isoformat(),
      "articles": final_articles
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
