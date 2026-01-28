import csv
import io
import urllib.request
from datetime import datetime, timezone

from LTTBalgrithm import largest_triangle_three_buckets


def _fetch_csv_text(url: str, timeout_seconds: int = 15) -> str:
    with urllib.request.urlopen(url, timeout=timeout_seconds) as response:
        return response.read().decode("utf-8")


def _parse_csv(csv_text: str):
    stream = io.StringIO(csv_text)
    reader = csv.reader(stream)

    header = next(reader, None)
    if header is None:
        raise ValueError("CSV appears empty")

    points = []
    first_ts = None
    last_ts = None

    row_number = 1
    for row in reader:
        if not row or len(row) < 2:
            continue

        ts = datetime.strptime(row[0], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        height = float(row[1])

        if first_ts is None:
            first_ts = ts
        last_ts = ts

        points.append((row_number, height))
        row_number += 1

    if not points or first_ts is None or last_ts is None:
        raise ValueError("CSV contained no data rows")

    return points, first_ts, last_ts


def _downsample_to_heights(points, threshold: int):
    if len(points) == threshold:
        downsampled = points
    else:
        downsampled = largest_triangle_three_buckets(points, threshold)

    heights = [round(float(p[1]), 2) for p in downsampled]
    if len(heights) != threshold:
        raise ValueError("Downsample did not return expected number of points")

    return heights


def build_river_level_document(stations, threshold: int = 200):
    now = datetime.now(timezone.utc)

    out = {
        "utc_time": now.isoformat(),
        "stations": [],
    }

    for station in stations:
        url = station.get("url")
        if not url:
            out["stations"].append(
                {
                    **station,
                    "error": "missing url",
                }
            )
            continue

        csv_text = _fetch_csv_text(url)
        points, first_ts, last_ts = _parse_csv(csv_text)

        if len(points) <= threshold:
            raise ValueError("Not enough data points to downsample")

        heights = _downsample_to_heights(points, threshold)

        out_station = {
            "name": station.get("name"),
            "url": url,
            "top_of_normal_range_m": station.get("top_of_normal_range_m"),
            "highest_ever_recorded_m": station.get("highest_ever_recorded_m"),
            "y_axis_top_m": station.get("y_axis_top_m"),
            "first_timestamp_utc": first_ts.isoformat(),
            "last_timestamp_utc": last_ts.isoformat(),
            "heights_m": heights,
        }

        out["stations"].append(out_station)

    return out
