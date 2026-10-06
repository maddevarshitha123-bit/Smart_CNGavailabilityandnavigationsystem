"""Generate SYNTHETIC CNG history data -> data/cng_history.csv

This is demonstration data (rule-based + random noise), NOT real station logs.
Run: python generate_dataset.py
"""

import numpy as np
import pandas as pd
from datetime import date, timedelta
from config import DATA_PATH


rng = np.random.default_rng(42)  # fixed seed -> same data every run


# Station popularity factors
STATIONS = {
    1: 1.0,
    2: 1.2,
    3: 1.5,
    4: 0.8,
    5: 1.3,
    6: 0.9
}
# Station information
STATION_INFO = [
    {
        "station_id": 1,
        "name": "Sample CNG - Tarnaka",
        "address": "Tarnaka, Hyderabad",
        "latitude": 17.4280,
        "longitude": 78.5310
    },
    {
        "station_id": 2,
        "name": "Sample CNG - Kukatpally",
        "address": "Kukatpally, Hyderabad",
        "latitude": 17.4849,
        "longitude": 78.4138
    },
    {
        "station_id": 3,
        "name": "Sample CNG - Gachibowli",
        "address": "Gachibowli, Hyderabad",
        "latitude": 17.4401,
        "longitude": 78.3489
    },
    {
        "station_id": 4,
        "name": "Sample CNG - Secunderabad",
        "address": "Secunderabad, Hyderabad",
        "latitude": 17.4399,
        "longitude": 78.4983
    },
    {
        "station_id": 5,
        "name": "Sample CNG - Mehdipatnam",
        "address": "Mehdipatnam, Hyderabad",
        "latitude": 17.3936,
        "longitude": 78.4397
    },
    {
        "station_id": 6,
        "name": "Sample CNG - LB Nagar",
        "address": "LB Nagar, Hyderabad",
        "latitude": 17.3457,
        "longitude": 78.5522
    }
]


HOURS = range(6, 22)  # 6 AM - 9 PM
DAYS = 30

AVAIL = {
    "Low": 0,
    "Medium": 1,
    "High": 2
}

AVAIL_NAME = {
    v: k for k, v in AVAIL.items()
}


def hourly_profile(hour, weekend):
    """Demand shape: morning + evening peaks on weekdays."""

    if weekend:
        return (
            0.5
            + 0.8 * np.exp(-((hour - 13) ** 2) / 12)
            + 0.6 * np.exp(-((hour - 18) ** 2) / 6)
        )

    return (
        0.4
        + 1.0 * np.exp(-((hour - 8.5) ** 2) / 5)
        + 1.1 * np.exp(-((hour - 18) ** 2) / 5)
    )


def traffic_from_demand(demand):
    """Generate traffic level from demand."""

    score = demand + rng.normal(0, 0.25)

    if score > 1.35:
        return "High"
    elif score > 0.85:
        return "Medium"
    else:
        return "Low"
def main():
    """Generate CNG history and station information CSV files."""

    start = date.today() - timedelta(days=DAYS)

    rows = []

    # Generate historical data
    for sid, pop in STATIONS.items():

        prev_wait = 10
        prev_av = 2

        for d in range(DAYS):

            day = start + timedelta(days=d)
            dow = day.weekday()
            weekend = int(dow >= 5)

            for h in HOURS:

                demand = hourly_profile(h, weekend) * pop

                # Vehicles arriving per hour
                vph = max(
                    2,
                    int(rng.poisson(demand * 18))
                )

                # Traffic
                traffic = traffic_from_demand(demand)

                t_factor = {
                    "Low": 0.9,
                    "Medium": 1.0,
                    "High": 1.25
                }[traffic]

                # Queue length
                queue = max(
                    0,
                    int(rng.poisson(vph * 0.32 * t_factor))
                )

                # Service time
                service = rng.normal(2.6, 0.4)

                # Waiting time
                wait = max(
                    0,
                    int(
                        queue * service
                        + 0.15 * prev_wait
                        + rng.normal(0, 2)
                    )
                )

                # Availability
                pressure = (
                    vph / 30
                    + (2 - prev_av) * 0.25
                    + rng.normal(0, 0.35)
                )

                if pressure > 1.25:
                    av = 0
                elif pressure > 0.75:
                    av = 1
                else:
                    av = 2

                rows.append(
                    {
                        "station_id": sid,
                        "date": day.isoformat(),
                        "hour": h,
                        "day_of_week": dow,
                        "is_weekend": weekend,
                        "queue_length": queue,
                        "traffic_level": traffic,
                        "vehicles_per_hour": vph,
                        "previous_waiting_time": prev_wait,
                        "previous_availability": AVAIL_NAME[prev_av],
                        "waiting_time": wait,
                        "availability": AVAIL_NAME[av]
                    }
                )

                prev_wait = wait
                prev_av = av

    # Convert history to DataFrame
    df = pd.DataFrame(rows)

    # Make sure data folder exists
    DATA_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # Save history data
    df.to_csv(
        DATA_PATH,
        index=False
    )

    # Save station information
    stations_df = pd.DataFrame(STATION_INFO)

    stations_file = DATA_PATH.parent / "cng_stations.csv"

    stations_df.to_csv(
        stations_file,
        index=False
    )

    # Print results
    print(f"Saved {len(df)} rows to {DATA_PATH}")
    print(
        f"Saved {len(stations_df)} stations to {stations_file}"
    )

    print("\nAvailability:")
    print(
        df["availability"].value_counts().to_string()
    )

    print("\nFirst 5 history records:")
    print(df.head())


if __name__ == "__main__":
    main()