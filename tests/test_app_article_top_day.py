from unittest.mock import patch

import pytest
from requests import Response

from app import app, V1_BASE_URL


GET_ARTICLE_TOP_DAY_URL = f"{V1_BASE_URL}/articles/top_day"
WIKIMEDIA_EMPTY_RESPONSE = {
    "detail": "The date(s) you used are valid, but we either do not have data for those date(s), or the project you asked for is not loaded yet."
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
def test_article_top_day(mock_request, client):
    response_with_json = Response()
    response_with_json.json = lambda: WIKIMEDIA_RESPONSE
    response_with_json.status_code = 200
    mock_request.return_value = response_with_json

    params = {"month": 10, "year": 2015, "title": "Carlos_Hathcock"}
    resp = client.get(GET_ARTICLE_TOP_DAY_URL, query_string=params)

    assert resp.json["title"] == params["title"]
    assert resp.json["date"] == "2015-10-10"
    assert resp.json["views"] == 291926


@patch("app.requests.get")
def test_article_top_day_no_data(mock_request, client):
    """
    Should return an empty response when the provided parameters are valid,
    but Wikimedia does not have any data loaded for that date and title.
    """
    response_with_json = Response()
    response_with_json.json = lambda: WIKIMEDIA_EMPTY_RESPONSE
    response_with_json.status_code = 404
    mock_request.return_value = response_with_json

    params = {"month": 10, "year": 2015, "title": "Carlos_Hathcock"}
    resp = client.get(GET_ARTICLE_TOP_DAY_URL, query_string=params)

    assert resp.json["title"] == params["title"]
    assert resp.json["date"] == None
    assert resp.json["views"] == 0


def test_article_top_day_bad_date_format(client):
    params = {"month": "October", "year": 2015, "title": "Carlos_Hathcock"}
    resp = client.get(GET_ARTICLE_TOP_DAY_URL, query_string=params)

    assert resp.status_code == 400
    assert resp.json["description"] == "Month and year must be integers"


def test_article_top_day_missing_required_params(client):
    params = {"month": 2, "year": 2021}
    resp = client.get(GET_ARTICLE_TOP_DAY_URL, query_string=params)

    assert resp.status_code == 400
    assert resp.json["description"] == "Must provide a title"
