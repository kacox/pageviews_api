from dataclasses import dataclass, InitVar
from datetime import date

from werkzeug.exceptions import BadRequest


def assert_date_components(*args):
    for arg in args:
        try:
            assert arg[0]
        except AssertionError:
            raise BadRequest(f"Must provide {arg[1]}")


def assert_title(title):
    try:
        assert title
    except AssertionError:
        raise BadRequest("Must provide a title")


def assert_week_has_day(day, time_period):
    """A day must be given when a week-long time period is requested."""
    if time_period.lower() == "week":
        try:
            assert day
        except AssertionError:
            raise BadRequest("Must have start day when requesting a week"
                             + " of articles")


def validate_date(day, month, year):
    try:
        date(year=year, month=month, day=day)
    except ValueError:
        raise BadRequest("Invalid date")


def validate_day_month_year(day, month, year):
    try:
        day = int(day)
        month = int(month)
        year = int(year)
        return day, month, year
    except ValueError:
        raise BadRequest("Day, month, and year must be integers")


def validate_time_period(time_period):
    try:
        assert time_period
    except AssertionError:
        raise BadRequest("Must provide a time_period")

    try:
        assert time_period.lower() == "month" or time_period.lower() == "week"
    except AssertionError:
        raise BadRequest("time_period must be 'month' or 'week'")


@dataclass
class GetMostViewedArticlesRequest:
    month: InitVar[int]
    year: InitVar[int]
    time_period: str
    day: InitVar[int | None] = None

    def __post_init__(self, month, year, day) -> None:
        validate_time_period(self.time_period)

        assert_date_components((month, "month"), (year, "year"))
        assert_week_has_day(day, self.time_period)

        if day:
            self.day, self.month, self.year = (
                validate_day_month_year(day, month, year)
            )
        else:
            self.day, self.month, self.year = (
                validate_day_month_year(1, month, year)
            )

        validate_date(self.day, self.month, self.year)


@dataclass
class GetTotalArticleViewsRequest:
    month: InitVar[int]
    year: InitVar[int]
    time_period: str
    title: str
    day: InitVar[int | None] = None

    def __post_init__(self, month, year, day) -> None:
        assert_title(self.title)

        validate_time_period(self.time_period)

        assert_date_components((month, "month"), (year, "year"))
        assert_week_has_day(day, self.time_period)

        if day:
            self.day, self.month, self.year = (
                validate_day_month_year(day, month, year)
            )
        else:
            self.day, self.month, self.year = (
                validate_day_month_year(1, month, year)
            )

        validate_date(self.day, self.month, self.year)


@dataclass
class GetArticleTopDayRequest:
    month: InitVar[int]
    year: InitVar[int]
    title: str

    def __post_init__(self, month, year) -> None:
        assert_title(self.title)

        assert_date_components((month, "month"), (year, "year"))

        try:
            self.month = int(month)
            self.year = int(year)
        except ValueError:
            raise BadRequest("Month and year must be integers")
