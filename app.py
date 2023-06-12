import bisect
import logging
import logging.config
from calendar import monthrange
from datetime import date, datetime, timedelta

import requests
from flask import json, request, Flask
from werkzeug.exceptions import BadRequest, HTTPException

from schemas import (
    GetArticleTopDayRequest,
    GetMostViewedArticlesRequest,
    GetTotalArticleViewsRequest
)


logging.config.fileConfig("logging.conf")
LOGGER = logging.getLogger("pageviewsApi")
USER_AGENT_HEADER = {'User-Agent': 'pageviewsAPI/0.0 (ka.cox@outlook.com)'}
V1_BASE_URL="/api/v1"
WIKIMEDIA_BASE_URL = "https://wikimedia.org/api/rest_v1"
WIKIMEDIA_TOP_PATH = "/metrics/pageviews/top"
WIKIMEDIA_ACCESS_PARAM = "all-access"
WIKIMEDIA_AGENT_PARAM = "all-agents"
WIKIMEDIA_GRANULARITY_PARAM = "daily"
WIKIMEDIA_PROJECT_PARAM = "en.wikipedia"
WIKIMEDIA_TIME_FORMAT = "%Y%m%d"

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
    LOGGER.info(f"Making {len(days)} requests to {WIKIMEDIA_BASE_URL}{WIKIMEDIA_TOP_PATH}")
    for day in days:
        resp = requests.get(
            f"{WIKIMEDIA_BASE_URL}{WIKIMEDIA_TOP_PATH}/"
            + f"{WIKIMEDIA_PROJECT_PARAM}/{WIKIMEDIA_ACCESS_PARAM}/"
            + f"{day.year}/{day.month}/{day.day}",
            headers=USER_AGENT_HEADER,
        )
        resp.raise_for_status()

        articles = resp.json()["items"][0]["articles"]
        for article in articles:
            article_counts[article["article"]] = article_counts.get(
                article["article"], 0
            ) + article["views"]
    final_articles = []
    for title, views in article_counts.items():
        element = {"title": title, "total_views": views}
        bisect.insort(
            final_articles,
            element,
            key=lambda element: -1 * element["total_views"]
        )

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

    if request_schema.time_period == "week":
        start_date = date(
            request_schema.year, request_schema.month, request_schema.day
        )
        end_date = start_date + timedelta(days=6)
    elif request_schema.time_period == "month":
        start_date = date(
            request_schema.year, request_schema.month, 1
        )
        remaining_month_days = monthrange(
            request_schema.year, request_schema.month
        )[1] - 1
        end_date = start_date + timedelta(days=remaining_month_days)

    resp = requests.get(
        f"{WIKIMEDIA_BASE_URL}/metrics/pageviews/per-article/"
        + f"{WIKIMEDIA_PROJECT_PARAM}/{WIKIMEDIA_ACCESS_PARAM}/"
        + f"{WIKIMEDIA_AGENT_PARAM}/{request_schema.title}/"
        + f"{WIKIMEDIA_GRANULARITY_PARAM}/"
        + f"{start_date.strftime(WIKIMEDIA_TIME_FORMAT)}/"
        + f"{end_date.strftime(WIKIMEDIA_TIME_FORMAT)}",
        headers=USER_AGENT_HEADER,
    )
    resp.raise_for_status()

    total_views = 0
    for entry in resp.json()["items"]:
        total_views += entry["views"]

    return {
      "title": request_schema.title,
      "start_date": start_date.isoformat(),
      "end_date": end_date.isoformat(),
      "total_views": total_views
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

    start_date = date(request_schema.year, request_schema.month, 1)
    remaining_month_days = monthrange(
        request_schema.year, request_schema.month
    )[1] - 1
    end_date = start_date + timedelta(days=remaining_month_days)

    resp = requests.get(
        f"{WIKIMEDIA_BASE_URL}/metrics/pageviews/per-article/"
        + f"{WIKIMEDIA_PROJECT_PARAM}/{WIKIMEDIA_ACCESS_PARAM}/"
        + f"{WIKIMEDIA_AGENT_PARAM}/{request_schema.title}/"
        + f"{WIKIMEDIA_GRANULARITY_PARAM}/"
        + f"{start_date.strftime(WIKIMEDIA_TIME_FORMAT)}/"
        + f"{end_date.strftime(WIKIMEDIA_TIME_FORMAT)}",
        headers=USER_AGENT_HEADER,
    )
    resp.raise_for_status()

    most_views = 0
    most_viewed_day = None
    for entry in resp.json()["items"]:
        if entry["views"] > most_views:
            most_views = entry["views"]
            most_viewed_day = entry["timestamp"]

    most_viewed_day = datetime.strptime(most_viewed_day, "%Y%m%d00")

    return {
      "title": request_schema.title,
      "date": most_viewed_day.strftime("%Y-%m-%d"),
      "views": most_views
    }
