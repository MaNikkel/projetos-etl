#!/usr/bin/env python3
import argparse
import json
import sys


METRIC_LABELS = {
    "mem_max": "Memory Max (%)",
    "mem_avg": "Memory Avg Peak (%)",
    "cpu_avg": "CPU Avg Peak (%)",
    "net_in_avg": "NetworkIn Avg Peak (bytes)",
    "net_out_avg": "NetworkOut Avg Peak (bytes)",
}

METRIC_ORDER = ["mem_max", "mem_avg", "cpu_avg", "net_in_avg", "net_out_avg"]
INSTANCE_ORDER = ["java", "haskell"]


def read_input(path):
    if path == "-":
        return json.load(sys.stdin)

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def format_value(value):
    if value is None:
        return "-"

    if abs(value) >= 1000:
        return f"{value:,.0f}"

    return f"{value:.2f}"


def parse_result_id(result_id):
    for instance in INSTANCE_ORDER:
        prefix = f"{instance}_"
        if result_id.startswith(prefix):
            return instance, result_id.removeprefix(prefix)

    return None, None


def build_table(data):
    values = {
        instance: {metric: None for metric in METRIC_ORDER}
        for instance in INSTANCE_ORDER
    }

    for result in data.get("MetricDataResults", []):
        instance, metric = parse_result_id(result.get("Id", ""))
        if instance not in values or metric not in values[instance]:
            continue

        metric_values = result.get("Values", [])
        if metric_values:
            values[instance][metric] = max(metric_values)

    rows = []
    for metric in METRIC_ORDER:
        rows.append([
            METRIC_LABELS[metric],
            format_value(values["java"][metric]),
            format_value(values["haskell"][metric]),
        ])

    return rows


def print_table(rows):
    headers = ["Metric", "Java", "Haskell"]
    all_rows = [headers, *rows]
    widths = [
        max(len(str(row[index])) for row in all_rows)
        for index in range(len(headers))
    ]

    def line(row):
        return " | ".join(str(value).ljust(widths[index]) for index, value in enumerate(row))

    print(line(headers))
    print("-+-".join("-" * width for width in widths))
    for row in rows:
        print(line(row))


def main():
    parser = argparse.ArgumentParser(
        description="Format AWS CloudWatch get-metric-data JSON as a max-value comparison table."
    )
    parser.add_argument(
        "input",
        nargs="?",
        default="-",
        help="Path to CloudWatch JSON file. Defaults to stdin.",
    )
    args = parser.parse_args()

    data = read_input(args.input)
    print_table(build_table(data))


if __name__ == "__main__":
    main()
