"""Generate valid and malformed inputs for all three bike share parsers."""

from hypothesis import given, settings, strategies as st

from bike_share_rental_parser import (
    format_station_code,
    parse_ride_duration,
    parse_ride_log,
)

NON_TEXT = st.one_of(st.none(), st.integers(), st.booleans(), st.binary())
BIKE_TYPES = st.sampled_from(("standard", "electric", "cargo"))


@settings(derandomize=True, report_multiple_bugs=False)
@given(
    hours=st.integers(0, 999),
    minutes=st.integers(0, 59),
    invalid=st.one_of(NON_TEXT, st.text(alphabet="0123456789")),
    overflow=st.integers(60, 99),
)
def test_parse_ride_duration(hours, minutes, invalid, overflow):
    assert parse_ride_duration(f" {hours:02}:{minutes:02} ") == hours * 60 + minutes
    assert parse_ride_duration(invalid) is None
    assert parse_ride_duration(f"{hours:02}:{overflow}") is None


@settings(derandomize=True, report_multiple_bugs=False)
@given(
    zone=st.sampled_from(tuple("abcdefghijklmnopqrstuvwxyz")),
    number=st.text(alphabet="0123456789", min_size=1, max_size=12),
    invalid=st.one_of(NON_TEXT, st.text().map(lambda text: "!" + text)),
)
def test_format_station_code(zone, number, invalid):
    assert format_station_code(f" {zone}{number} ") == f"{zone.upper()}-{number}"
    assert format_station_code(invalid) is None
    assert format_station_code("") is None


@settings(derandomize=True, report_multiple_bugs=False)
@given(
    bike=BIKE_TYPES,
    minutes=st.integers(1, 10000),
    subscriber=st.booleans(),
    invalid=st.one_of(NON_TEXT, st.text(alphabet="0123456789")),
)
def test_parse_ride_log(bike, minutes, subscriber, invalid):
    flag = "yes" if subscriber else "no"
    assert parse_ride_log(f" {bike}, {minutes}, {flag} ") == (bike, minutes, subscriber)
    assert parse_ride_log(invalid) is None
    assert parse_ride_log(f"{bike},{minutes},maybe") is None
    assert parse_ride_log(f"{bike},{minutes},{flag},extra") is None
    assert parse_ride_log(f"{bike},0,{flag}") is None
    assert parse_ride_log(f"tandem,{minutes},{flag}") is None
