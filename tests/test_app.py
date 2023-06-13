from datetime import date

import pytest

from app import calculate_days, calculate_start_and_end_date


def test_calculate_days_week():
    days = calculate_days("week", 2023, 6, 1)

    assert len(days) == 7
    assert days[0] == date(2023, 6, 1)
    assert days[1] == date(2023, 6, 2)
    assert days[-1] == date(2023, 6, 7)


def test_calculate_days_week_missing_day():
    with pytest.raises(ValueError) as excinfo:
        days = calculate_days("week", 2023, 6, None)

    assert "Must provide day" in str(excinfo.value)


def test_calculate_days_month():
    days = calculate_days("month", 2023, 6, None)

    assert len(days) == 30
    assert days[0] == date(2023, 6, 1)
    assert days[1] == date(2023, 6, 2)
    assert days[-1] == date(2023, 6, 30)


def test_calculate_days_month_leap_year():
    days = calculate_days("month", 2020, 2, None)

    assert len(days) == 29
    assert days[0] == date(2020, 2, 1)
    assert days[1] == date(2020, 2, 2)
    assert days[-1] == date(2020, 2, 29)


def test_calculate_days_bad_time_period():
    with pytest.raises(ValueError) as excinfo:
        calculate_days("year", 2023, 6, 1)

    assert "time_period" in str(excinfo.value)


def test_calculate_start_and_end_date_week():
    start_date, end_date = calculate_start_and_end_date("week", 2023, 9, 10)

    assert start_date == date(2023, 9, 10)
    assert end_date == date(2023, 9, 16)


def test_calculate_start_and_end_date_week_missing_day():
    with pytest.raises(ValueError) as excinfo:
        calculate_start_and_end_date("week", 2023, 9, None)

    assert "Must provide day" in str(excinfo.value)


def test_calculate_start_and_end_date_month():
    start_date, end_date = calculate_start_and_end_date("month", 2023, 9, None)

    assert start_date == date(2023, 9, 1)
    assert end_date == date(2023, 9, 30)


def test_calculate_start_and_end_date_month_leap_year():
    start_date, end_date = calculate_start_and_end_date("month", 2020, 2, None)

    assert start_date == date(2020, 2, 1)
    assert end_date == date(2020, 2, 29)


def test_calculate_days_bad_time_period():
    with pytest.raises(ValueError) as excinfo:
        calculate_start_and_end_date("year", 2020, 2, None)

    assert "time_period" in str(excinfo.value)
