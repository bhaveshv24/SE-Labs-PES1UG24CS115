# Lab 7 — Bike Share Rental

The parser uses the three functions from the assigned Lab 7 starter
(upstream commit `066cd16`). Invalid input returns `None` and the
interactive program displays `Invalid input`.

From this directory, run:

```sh
python -m pip install -r requirements.txt
python bike_share_rental_parser.py
python -m pytest -q test_bike_share_rental_parser.py
```

The Hypothesis suite checks valid results and rejection of malformed
values for ride durations, station codes and ride logs.
