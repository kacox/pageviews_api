# Pageviews API

A simple Flask webservice that can gather Wikimedia article data.

## Setup

Create a virtual environment and install the packages specified in the
`requirements.txt` file.

Run the webserver using:
```
flask run [--reload | --debug]
```

## API

### `GET /api/v1/articles/top`

Retrieves a list of the most viewed articles for a given week or month.

```
Query parameters:
    *time_period : "week" or "month"
    day: number representing a day of the month; only required when time_period
        is a "week"
    *month: number (1-12) representing a month of the year
    *year: a four digit number representing a year

*required

Example request:
    http://127.0.0.1:5000/api/v1/articles/top?day=15&month=3&time_period=week&year=2020

Example response:
    {
      "articles": [
        {
          "title": "Main_Page",
          "total_views": 68235670
        },
        {
          "title": "United_States_Senate",
          "total_views": 24670208
        },
        {
          "title": "Special:Search",
          "total_views": 10930695
        },
        {
          "title": "2019–20_coronavirus_pandemic",
          "total_views": 7645103
        },
        {
          "title": "Coronavirus",
          "total_views": 2749576
        },
        ...
      ],
      "count": 2066,
      "end_date": "2020-03-21",
      "start_date": "2020-03-15"
    }
```

### `GET /api/v1/articles/total_views`

For an article, get the total views for that article in a given a week or a
month.

```
Query parameters:
    *time_period : "week" or "month"
    day: number representing a day of the month; only required when time_period
        is a "week"
    *month: number (1-12) representing a month of the year
    *year: a four digit number representing a year
    *title: the title of an article

*required

Example request:
    http://127.0.0.1:5000/api/v1/articles/total_views?day=1&month=6&year=2021&time_period=week&title=Coronavirus

Example response:
    {
      "end_date": "2021-06-07",
      "start_date": "2021-06-01",
      "title": "Coronavirus",
      "total_views": 71452
    }
```

### `GET /api/v1/articles/top_day`

For an article in a given month, return which day it got the most views.

```
Query parameters:
    *month: number (1-12) representing a month of the year
    *year: a four digit number representing a year
    *title: the title of an article

*required

Example request:
    http://127.0.0.1:5000/api/v1/articles/top_day?month=6&year=2021&title=Coronavirus

Example response:
    {
      "date": "2021-06-01",
      "title": "Coronavirus",
      "views": 11830
    }
```

## Development

To run tests, from the top level directory execute:
```
python -m pytest
```

## Additional info

This webservice uses the [Wikimedia REST API](https://wikimedia.org/api/rest_v1/)
provided by the Wikimedia Services team to lookup article data.
