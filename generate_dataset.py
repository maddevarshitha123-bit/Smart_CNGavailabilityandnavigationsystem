"""Generate SYNTHETIC CNG history data -> data/cng_history.csv

This is demonstration data (rule-based + random noise), NOT real station logs.
Run:  python generate_dataset.py
"""
import numpy as np
import pandas as pd
from datetime import date, timedelta
from config import DATA_PATH

rng = np.random.default_rng(42)          # fixed seed -> same data every run

STATIONS = {1: 1.0, 2: 1.2, 3: 1.5, 4: 0.8, 5: 1.3, 6: 0.9}   # station popularity factor
HOURS = range(6, 22)                                            # 6 AM - 9 PM
DAYS = 30
AVAIL = {"Low": 0, "Medium": 1, "High": 2}
AVAIL_NAME = {v: k for k, v in AVAIL.items()}


def hourly_profile(hour, weekend):
    """Demand shape: morning + evening peaks on weekdays, afternoon bump on weekends."""
    if weekend:
        return 0.5 + 0.8 * np.exp(-((hour - 13) ** 2) / 12) + 0.6 * np.exp(-((hour - 18) ** 2) / 6)
    return (0.4 + 1.0 * np.exp(-((hour - 8.5) ** 2) / 5)
            + 1.1 * np.exp(-((hour - 18) ** 2) / 5))


def traffic_from_demand(demand):
    score = demand + rng.normal(0, 0.25)
    return "High" if score > 1.35 else ("Medium" if score > 0.85 else "Low")


def main():
    start = date.today() - timedelta(days=DAYS)
    rows = []
    for sid, pop in STATIONS.items():
        prev_wait, prev_av = 10, 2                     # starting state
        for d in range(DAYS):
            day = start + timedelta(days=d)
            dow = day.weekday()
            weekend = int(dow >= 5)
            for h in HOURS:
                demand = hourly_profile(h, weekend) * pop
                vph = max(2, int(rng.poisson(demand * 18)))               # vehicles arriving / hour
                traffic = traffic_from_demand(demand)
                t_factor = {"Low": 0.9, "Medium": 1.0, "High": 1.25}[traffic]
                queue = max(0, int(rng.poisson(vph * 0.32 * t_factor)))
                service = rng.normal(2.6, 0.4)                            # minutes per vehicle
                wait = max(0, int(queue * service + 0.15 * prev_wait + rng.normal(0, 2)))
                pressure = vph / 30 + (2 - prev_av) * 0.25 + rng.normal(0, 0.35)
                av = 0 if pressure > 1.25 else (1 if pressure > 0.75 else 2)
                rows.append(dict(
                    station_id=sid, date=day.isoformat(), hour=h, day_of_week=dow,
                    is_weekend=weekend, queue_length=queue, traffic_level=traffic,
                    vehicles_per_hour=vph, previous_waiting_time=prev_wait,
                    previous_availability=AVAIL_NAME[prev_av], waiting_time=wait,
                    availability=AVAIL_NAME[av]))
                prev_wait, prev_av = wait, av
    df = pd.DataFrame(rows)
    DATA_PATH.parent.mkdir(exist_ok=True)
    df.to_csv(DATA_PATH, index=False)
    print(f"Saved {len(df)} rows to {DATA_PATH}")
    print(df["availability"].value_counts().to_string())
    print(df.head())


if __name__ == "__main__":
    main()
