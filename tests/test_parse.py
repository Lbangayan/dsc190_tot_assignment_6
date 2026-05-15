from datetime import date
from nldate import parse


def test_exact_date_verbose():
    assert parse("December 1st, 2025") == date(2025, 12, 1)


def test_exact_date_short():
    assert parse("Jan 5 2024") == date(2024, 1, 5)


def test_exact_date_numerical():
    assert parse("10/31/2023") == date(2023, 10, 31)


def test_implicit_year():
    reference = date(2026, 5, 14)
    # When the year is omitted, it should default to the reference year
    assert parse("August 15th", reference) == date(2026, 8, 15)


def test_tomorrow():
    reference = date(2026, 5, 14)
    assert parse("tomorrow", reference) == date(2026, 5, 15)


def test_yesterday():
    reference = date(2026, 5, 14)
    assert parse("yesterday", reference) == date(2026, 5, 13)


def test_in_x_days():
    reference = date(2026, 5, 14)
    assert parse("in 3 days", reference) == date(2026, 5, 17)


def test_a_week_ago():
    reference = date(2026, 5, 14)
    assert parse("a week ago", reference) == date(2026, 5, 7)


def test_x_weeks_from_today():
    reference = date(2026, 5, 14)
    assert parse("2 weeks from today", reference) == date(2026, 5, 28)


def test_x_weeks_from_now():
    reference = date(2026, 5, 14)
    assert parse("2 weeks from now", reference) == date(2026, 5, 28)


def test_relative_days_before_date():
    reference = date(2025, 12, 6)
    assert parse("5 days before December 1st, 2025", reference) == date(2025, 11, 26)


def test_complex_relative_after_yesterday():
    reference = date(2025, 5, 15)
    # Yesterday is May 14, 2025. 1 year and 2 months later is July 14, 2026.
    assert parse("1 year and 2 months after yesterday", reference) == date(2026, 7, 14)


def test_next_weekday():
    # If today is Monday, May 11, 2026, next Tuesday is May 12.
    reference = date(2026, 5, 11)
    assert parse("next Tuesday", reference) == date(2026, 5, 12)


def test_last_weekday():
    # If today is Thursday, May 14, 2026, last Friday was May 8.
    reference = date(2026, 5, 14)
    assert parse("last Friday", reference) == date(2026, 5, 8)


def test_case_and_punctuation_insensitivity():
    reference = date(2026, 5, 11)
    assert parse("NeXT tUesDay!!!", reference) == date(2026, 5, 12)


def test_default_today():
    # If no 'today' is provided, it should default to the actual current system date.
    # We test this by checking "today" and comparing it to date.today()
    assert parse("today") == date.today()
