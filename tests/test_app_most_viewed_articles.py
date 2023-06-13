from unittest.mock import patch

import pytest
from requests import Response

from app import app, V1_BASE_URL


GET_MOST_VIEWED_ARTICLES_URL = f"{V1_BASE_URL}/articles/top"
WIKIMEDIA_RESPONSE = {
    "items": [
        {
            "project": "en.wikipedia",
            "access": "all-access",
            "year": "2015",
            "month": "10",
            "day": "10",
            "articles": [
                {
                    "article": "Main_Page",
                    "views": 18793503,
                    "rank": 1
                },
                {
                    "article": "Special:Search",
                    "views": 2629537,
                    "rank": 2
                },
                {
                    "article": "Carlos_Hathcock",
                    "views": 291358,
                    "rank": 3
                },
            ]
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
def test_most_viewed_articles_week(mock_request, client):
    response_with_json = Response()
    response_with_json.json = lambda: WIKIMEDIA_RESPONSE
    response_with_json.status_code = 200
    mock_request.return_value = response_with_json

    params = {"day": 10, "month": 10, "year": 2015, "time_period": "week"}
    resp = client.get(GET_MOST_VIEWED_ARTICLES_URL, query_string=params)

    assert resp.json["start_date"] == "2015-10-10"
    assert resp.json["end_date"] == "2015-10-16"
    assert len(resp.json["articles"]) == resp.json["count"]


@patch("app.requests.get")
def test_most_viewed_articles_month(mock_request, client):
    response_with_json = Response()
    response_with_json.json = lambda: WIKIMEDIA_RESPONSE
    response_with_json.status_code = 200
    mock_request.return_value = response_with_json

    params = {"month": 10, "year": 2015, "time_period": "month"}
    resp = client.get(GET_MOST_VIEWED_ARTICLES_URL, query_string=params)

    assert resp.json["start_date"] == "2015-10-01"
    assert resp.json["end_date"] == "2015-10-31"
    assert len(resp.json["articles"]) == resp.json["count"]


def test_most_viewed_articles_bad_time_period(client):
    params = {"month": 10, "year": 2015, "time_period": "year"}
    resp = client.get(GET_MOST_VIEWED_ARTICLES_URL, query_string=params)

    assert resp.status_code == 400
    assert "time_period" in resp.json["description"]


def test_most_viewed_articles_bad_date_format(client):
    params = {"month": "October", "year": 2015, "time_period": "month"}
    resp = client.get(GET_MOST_VIEWED_ARTICLES_URL, query_string=params)

    assert resp.status_code == 400
    assert resp.json["description"] == "Day, month, and year must be integers"


def test_most_viewed_articles_invalid_date(client):
    params = {"day": 29, "month": 2, "year": 2021, "time_period": "week"}
    resp = client.get(GET_MOST_VIEWED_ARTICLES_URL, query_string=params)

    assert resp.status_code == 400
    assert resp.json["description"] == "Invalid date"


def test_most_viewed_articles_missing_day_when_requesting_week(client):
    params = {"month": 2, "year": 2021, "time_period": "week"}
    resp = client.get(GET_MOST_VIEWED_ARTICLES_URL, query_string=params)

    assert resp.status_code == 400
    assert "Must have start day" in resp.json["description"]


def test_most_viewed_articles_missing_required_params(client):
    params = {"day": 28, "month": 2, "year": 2021}
    resp = client.get(GET_MOST_VIEWED_ARTICLES_URL, query_string=params)

    assert resp.status_code == 400
    assert resp.json["description"] == "Must provide a time_period"
