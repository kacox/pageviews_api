from unittest.mock import patch

import pytest
from requests import Response

from app import app, V1_BASE_URL


GET_TOTAL_ARTICLE_VIEWS = f"{V1_BASE_URL}/articles/total_views"
WIKIMEDIA_EMPTY_RESPONSE = {
    "detail": "The date(s) you used are valid, but..."
}
WIKIMEDIA_RESPONSE = {
    "items": [
        {
            "project": "en.wikipedia",
            "article": "Carlos_Hathcock",
            "granularity": "daily",
            "timestamp": "2015101000",
            "access": "all-access",
            "agent": "all-agents",
            "views": 291926
        },
        {
            "project": "en.wikipedia",
            "article": "Carlos_Hathcock",
            "granularity": "daily",
            "timestamp": "2015101100",
            "access": "all-access",
            "agent": "all-agents",
            "views": 13380
        }
    ]
}


app.config.update({
        "TESTING": True,
    })


@pytest.fixture()
def client():
    return app.test_client()


@patch("app.requests.get")
def test_total_article_views_week(mock_request, client):
    response_with_json = Response()
    response_with_json.json = lambda: WIKIMEDIA_RESPONSE
    response_with_json.status_code = 200
    mock_request.return_value = response_with_json

    params = {
        "day": 10,
        "month": 10,
        "year": 2015,
        "time_period": "week",
        "title": "Carlos_Hathcock"
    }
    resp = client.get(GET_TOTAL_ARTICLE_VIEWS, query_string=params)

    assert resp.json["start_date"] == "2015-10-10"
    assert resp.json["end_date"] == "2015-10-16"
    assert resp.json["total_views"] == 305306
    assert resp.json["title"] == params["title"]


@patch("app.requests.get")
def test_total_article_views_week_no_data(mock_request, client):
    """
    Should return a response with 0 views when the provided parameters are
    valid, but Wikimedia does not have any data loaded for that date and title.
    """
    response_with_json = Response()
    response_with_json.json = lambda: WIKIMEDIA_EMPTY_RESPONSE
    response_with_json.status_code = 404
    mock_request.return_value = response_with_json

    params = {
        "day": 10,
        "month": 10,
        "year": 2015,
        "time_period": "week",
        "title": "Carlos_Hathcock"
    }
    resp = client.get(GET_TOTAL_ARTICLE_VIEWS, query_string=params)

    assert resp.json["start_date"] == "2015-10-10"
    assert resp.json["end_date"] == "2015-10-16"
    assert resp.json["total_views"] == 0
    assert resp.json["title"] == params["title"]


@patch("app.requests.get")
def test_total_article_views_month(mock_request, client):
    response_with_json = Response()
    response_with_json.json = lambda: WIKIMEDIA_RESPONSE
    response_with_json.status_code = 200
    mock_request.return_value = response_with_json

    params = {
        "month": 10,
        "year": 2015,
        "time_period": "month",
        "title": "Carlos_Hathcock"
    }
    resp = client.get(GET_TOTAL_ARTICLE_VIEWS, query_string=params)

    assert resp.json["start_date"] == "2015-10-01"
    assert resp.json["end_date"] == "2015-10-31"
    assert resp.json["total_views"] == 305306
    assert resp.json["title"] == params["title"]


def test_total_article_views_bad_date_format(client):
    params = {
        "month": "February",
        "year": 2015,
        "time_period": "month",
        "title": "Carlos_Hathcock"
    }
    resp = client.get(GET_TOTAL_ARTICLE_VIEWS, query_string=params)

    assert resp.status_code == 400
    assert resp.json["description"] == "Day, month, and year must be integers"


def test_total_article_views_bad_time_period(client):
    params = {
        "month": 10,
        "year": 2015,
        "time_period": "year",
        "title": "Carlos_Hathcock"
    }
    resp = client.get(GET_TOTAL_ARTICLE_VIEWS, query_string=params)

    assert resp.status_code == 400
    assert "time_period" in resp.json["description"]


def test_total_article_views_invalid_date(client):
    params = {
        "day": 29,
        "month": 2,
        "year": 2021,
        "time_period": "week",
        "title": "Carlos_Hathcock"
    }
    resp = client.get(GET_TOTAL_ARTICLE_VIEWS, query_string=params)

    assert resp.status_code == 400
    assert resp.json["description"] == "Invalid date"


def test_total_article_views_missing_day_when_requesting_week(client):
    params = {
        "month": 2,
        "year": 2021,
        "time_period": "week",
        "title": "Carlos_Hathcock"
    }
    resp = client.get(GET_TOTAL_ARTICLE_VIEWS, query_string=params)

    assert resp.status_code == 400
    assert "Must have start day" in resp.json["description"]


def test_total_article_views_missing_required_params_time_period(client):
    params = {
        "day": 29,
        "month": 2,
        "year": 2021,
        "title": "Carlos_Hathcock"
    }
    resp = client.get(GET_TOTAL_ARTICLE_VIEWS, query_string=params)

    assert resp.status_code == 400
    assert resp.json["description"] == "Must provide a time_period"


def test_total_article_views_missing_required_params_title(client):
    params = {
        "day": 29,
        "month": 2,
        "year": 2021,
        "time_period": "week",
    }
    resp = client.get(GET_TOTAL_ARTICLE_VIEWS, query_string=params)

    assert resp.status_code == 400
    assert resp.json["description"] == "Must provide a title"
