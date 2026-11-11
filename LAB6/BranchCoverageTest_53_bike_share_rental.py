"""Stage 2: retain stage 1 and add decision and boundary assertions."""

import pytest

from bike_share_rental import can_unlock, dock_status, ride_cost
from CodeCoverageTest_53_bike_share_rental import (  # noqa: F401
    test_dock_errors,
    test_dock_status_statements,
    test_ride_cost_errors,
    test_ride_cost_statements,
    test_unlock_statements,
)


@pytest.mark.parametrize(
    "bike, minutes, subscriber, peak, expected",
    [
        ("standard", 1, False, False, 20),
        ("standard", 29, False, False, 20),
        ("standard", 30, False, False, 20),
        ("standard", 31, False, False, 40),
        ("standard", 60, False, False, 40),
        ("standard", 61, False, False, 60),
        ("electric", 30, False, False, 35),
        ("cargo", 30, False, False, 50),
        ("standard", 1, True, True, 0),
        ("electric", 30, True, True, 0),
        ("standard", 31, True, False, 20),
        ("cargo", 60, True, True, 50),
        ("standard", 30, False, True, 35),
        ("cargo", 30, False, True, 50),
        ("standard", 180, False, False, 120),
        ("standard", 181, False, False, 240),
        ("electric", 181, True, True, 325),
    ],
)
def test_ride_boundaries(bike, minutes, subscriber, peak, expected):
    assert ride_cost(bike, minutes, subscriber, peak) == expected


@pytest.mark.parametrize("minutes", [-1, -30])
def test_negative_duration(minutes):
    with pytest.raises(ValueError, match="^invalid duration$"):
        ride_cost("standard", minutes, False, False)


@pytest.mark.parametrize("bikes, capacity", [(0, -1), (11, 10)])
def test_remaining_dock_error_paths(bikes, capacity):
    message = "invalid capacity" if capacity <= 0 else "invalid bike count"
    with pytest.raises(ValueError, match=f"^{message}$"):
        dock_status(bikes, capacity)


@pytest.mark.parametrize(
    "bikes, capacity, expected",
    [
        (1, 10, "few bikes"),
        (3, 10, "available"),
        (7, 10, "available"),
        (9, 10, "few slots"),
        (0, 1, "empty"),
        (1, 1, "full"),
        (1, 3, "few bikes"),
        (3, 4, "few slots"),
    ],
)
def test_dock_boundaries_and_precedence(bikes, capacity, expected):
    assert dock_status(bikes, capacity) == expected


@pytest.mark.parametrize(
    "balance, active, age, expected",
    [
        (1000, True, 15, False),
        (1000, True, 18, False),
        (1000, False, 15, False),
        (99, False, 16, False),
        (100, False, 16, True),
        (99, False, 17, False),
        (100, False, 17, True),
        (49, False, 18, False),
        (50, False, 18, True),
        (-1, False, 30, False),
        (51, False, 30, True),
    ],
)
def test_unlock_boundaries(balance, active, age, expected):
    assert can_unlock(balance, active, age) is expected
