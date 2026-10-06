"""Station service using CSV data."""

from datetime import datetime
from pathlib import Path

import pandas as pd

from utils.distance import (
    haversine,
    estimate_travel_minutes,
    navigation_url,
)

from ml.predict import predict, ModelMissingError


# Project folder
BASE_DIR = Path(__file__).resolve().parent.parent

# Data folder
DATA_DIR = BASE_DIR / "data"


def load_station_data():
    """Load station and history data from CSV files."""

    stations_file = DATA_DIR / "cng_stations.csv"
    history_file = DATA_DIR / "cng_history.csv"

    if not stations_file.exists():
        raise FileNotFoundError(
            "cng_stations.csv not found. "
            "Run: python generate_dataset.py"
        )

    stations = pd.read_csv(stations_file)

    # Load historical data
    if history_file.exists():

        history = pd.read_csv(history_file)

        # Get latest record for each station
        if "date" in history.columns:
            history = history.sort_values(
                ["station_id", "date", "hour"]
            )

        history = history.drop_duplicates(
            subset=["station_id"],
            keep="last"
        )

        columns = [
            "station_id",
            "availability",
            "queue_length",
            "waiting_time",
            "traffic_level",
        ]

        available_columns = [
            column
            for column in columns
            if column in history.columns
        ]

        stations = stations.merge(
            history[available_columns],
            on="station_id",
            how="left",
        )

    # Add missing status column
    if "status" not in stations.columns:
        stations["status"] = "open"

    stations["status"] = (
        stations["status"]
        .fillna("open")
        .astype(str)
        .str.lower()
    )

    # Add missing phone column
    if "phone" not in stations.columns:
        stations["phone"] = "N/A"

    # Add missing operating hours column
    if "operating_hours" not in stations.columns:
        stations["operating_hours"] = "06:00-22:00"

    # Add missing updated_at column
    if "updated_at" not in stations.columns:
        stations["updated_at"] = None

    # Handle empty values
    stations["phone"] = (
        stations["phone"]
        .fillna("N/A")
    )

    stations["operating_hours"] = (
        stations["operating_hours"]
        .fillna("06:00-22:00")
    )

    return stations


def enrich_stations(user_lat, user_lon, now=None):
    """Add distance, travel time and AI prediction."""

    now = now or datetime.now()

    stations = load_station_data()

    output = []

    for _, station in stations.iterrows():

        try:
            latitude = float(
                station["latitude"]
            )

            longitude = float(
                station["longitude"]
            )

        except (
            KeyError,
            TypeError,
            ValueError
        ):
            continue

        # Calculate distance
        distance = haversine(
            user_lat,
            user_lon,
            latitude,
            longitude,
        )

        # Station values
        queue = station.get(
            "queue_length",
            0
        )

        traffic = station.get(
            "traffic_level",
            "Medium"
        )

        waiting_time = station.get(
            "waiting_time",
            10
        )

        availability = station.get(
            "availability",
            "Medium"
        )

        status = station.get(
            "status",
            "open"
        )

        # Handle missing values
        if pd.isna(queue):
            queue = 0

        if pd.isna(traffic):
            traffic = "Medium"

        if pd.isna(waiting_time):
            waiting_time = 10

        if pd.isna(availability):
            availability = "Medium"

        if pd.isna(status):
            status = "open"

        # Convert queue to integer
        try:
            queue = int(queue)
        except (
            TypeError,
            ValueError
        ):
            queue = 0

        # Convert waiting time to float
        try:
            waiting_time = float(
                waiting_time
            )
        except (
            TypeError,
            ValueError
        ):
            waiting_time = 10

        # Convert status to string
        status = str(status).lower()

        # Create station result
        item = {
            **station.to_dict(),

            "latitude": latitude,
            "longitude": longitude,

            "distance_km": round(
                distance,
                2
            ),

            "travel_min": estimate_travel_minutes(
                distance
            ),

            "queue": queue,

            "traffic": traffic,

            "admin_availability": availability,

            "admin_wait": waiting_time,

            "status": status,

            "nav_url": navigation_url(
                latitude,
                longitude,
                user_lat,
                user_lon,
            ),
        }

        # AI prediction
        try:

            prediction = predict(
                station["station_id"],
                now.hour,
                now.weekday(),
                queue,
                traffic,
                max(2, queue * 3),
                waiting_time,
                availability,
            )

            item.update(
                pred_availability=prediction[
                    "availability"
                ],

                pred_wait=prediction[
                    "waiting_time"
                ],

                confidence=prediction[
                    "confidence"
                ],

                ml_ok=True,
            )

        except ModelMissingError:

            item.update(
                pred_availability=availability,

                pred_wait=waiting_time,

                confidence=None,

                ml_ok=False,
            )

        output.append(item)

    # Sort stations by nearest distance
    output.sort(
        key=lambda x: x["distance_km"]
    )

    return output