"""Stage 1: exercise every executable application statement."""

import pytest

from bike_share_rental import can_unlock, dock_status, ride_cost


@pytest.mark.parametrize(
    "bike, minutes, subscriber, peak, expected",
    [
        ("standard", 45, False, False, 40),
        ("standard", 30, True, False, 0),
        ("electric", 60, True, True, 50),
        ("cargo", 181, False, False, 450),
    ],
)
def test_ride_cost_statements(bike, minutes, subscriber, peak, expected):
    assert ride_cost(bike, minutes, subscriber, peak) == expected


@pytest.mark.parametrize(
    "bike, minutes, message",
    [
        ("tandem", 30, "unknown bike type"),
        ("standard", 0, "invalid duration"),
    ],
)
def test_ride_cost_errors(bike, minutes, message):
    with pytest.raises(ValueError, match=f"^{message}$"):
        ride_cost(bike, minutes, False, False)


@pytest.mark.parametrize(
    "bikes, capacity, expected",
    [
        (0, 10, "empty"),
        (10, 10, "full"),
        (2, 10, "few bikes"),
        (8, 10, "few slots"),
        (5, 10, "available"),
    ],
)
def test_dock_status_statements(bikes, capacity, expected):
    assert dock_status(bikes, capacity) == expected


@pytest.mark.parametrize(
    "bikes, capacity, message",
    [
        (0, 0, "invalid capacity"),
        (-1, 10, "invalid bike count"),
    ],
)
def test_dock_errors(bikes, capacity, message):
    with pytest.raises(ValueError, match=f"^{message}$"):
        dock_status(bikes, capacity)


@pytest.mark.parametrize(
    "balance, active, age, expected",
    [
        (200, True, 25, False),
        (200, False, 15, False),
        (100, False, 16, True),
        (50, False, 18, True),
    ],
)
def test_unlock_statements(balance, active, age, expected):
    assert can_unlock(balance, active, age) is expected
