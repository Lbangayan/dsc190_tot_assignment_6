import re
import calendar
from datetime import date, timedelta, datetime
from dateutil import parser as dt_parser
from dateutil.relativedelta import relativedelta


def parse(s: str, today: date | None = None) -> date:
    """
    Parses a natural language date string into a datetime.date object.
    """
    if today is None:
        today = date.today()

    # Clean string: lowercase and remove excessive punctuation
    # We keep spaces, slashes, commas, and hyphens for dateutil
    s_clean = re.sub(r"[^\w\s/,-]", "", s.lower().strip())

    # 1. Base relative words
    if s_clean == "today":
        return today
    if s_clean == "tomorrow":
        return today + timedelta(days=1)
    if s_clean == "yesterday":
        return today - timedelta(days=1)

    # 2. Weekdays (next / last)
    weekdays = {day.lower(): i for i, day in enumerate(calendar.day_name)}
    weekday_match = re.search(r"(next|last)\s+([a-z]+)", s_clean)
    if weekday_match:
        direction, day_str = weekday_match.groups()
        if day_str in weekdays:
            target_weekday = weekdays[day_str]
            current_weekday = today.weekday()

            if direction == "next":
                days_ahead = target_weekday - current_weekday
                if days_ahead <= 0:
                    days_ahead += 7
                return today + timedelta(days=days_ahead)
            else:  # last
                days_behind = current_weekday - target_weekday
                if days_behind <= 0:
                    days_behind += 7
                return today - timedelta(days=days_behind)

    # 3. Relative offsets logic
    def parse_delta(delta_str: str) -> relativedelta:
        """Helper to turn '1 year and 2 months' into a relativedelta object."""
        kwargs = {}
        # Find all occurrences of number + unit (e.g., '2 months', '1 year')
        for match in re.finditer(r"(\d+)\s+(year|month|week|day)s?", delta_str):
            val, unit = match.groups()
            if unit == "week":
                kwargs["days"] = kwargs.get("days", 0) + int(val) * 7
            else:
                kwargs[unit + "s"] = int(val)
        return relativedelta(**kwargs)

    # Complex recursive patterns: "X time before Y date" or "X time after Y date"
    complex_match = re.search(r"(.+?)\s+(before|after)\s+(.+)", s_clean)
    if complex_match:
        delta_str, direction, base_str = complex_match.groups()

        # Recursively evaluate the base date (e.g., turns "yesterday" into a real date)
        base_date = parse(base_str, today)
        delta = parse_delta(delta_str)

        if direction == "before":
            return base_date - delta
        else:
            return base_date + delta

    # "in X days/weeks/months"
    in_match = re.search(r"in\s+(.+)", s_clean)
    if in_match:
        return today + parse_delta(in_match.group(1))

    # "X days/weeks/months from today"
    from_match = re.search(r"(.+?)\s+from\s+today", s_clean)
    if from_match:
        return today + parse_delta(from_match.group(1))

    # 4. Absolute dates fallback
    try:
        # The default parameter ensures missing years default to the 'today' year
        parsed_dt = dt_parser.parse(
            s_clean, default=datetime(today.year, today.month, today.day)
        )
        return parsed_dt.date()
    except ValueError:
        pass

    raise ValueError(f"Could not parse date string: {s}")
