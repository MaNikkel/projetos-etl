#!/usr/bin/env python3
import argparse
import json
import shutil
import subprocess
import sys
from statistics import mean


DEFAULT_REGION = "us-east-1"
DEFAULT_NAMESPACE = "mestrado-etl"
DEFAULT_JAVA_INSTANCE_ID = "i-0077b2e8f26a71c34"
DEFAULT_HASKELL_INSTANCE_ID = "i-0ba27fb030a44a53d"

METRICS = [
    ("mem_max", "mestrado-etl", "mem_used_percent", "Maximum"),
    ("mem_avg", "mestrado-etl", "mem_used_percent", "Average"),
    ("cpu_avg", "AWS/EC2", "CPUUtilization", "Average"),
    ("net_in_avg", "AWS/EC2", "NetworkIn", "Average"),
    ("net_out_avg", "AWS/EC2", "NetworkOut", "Average"),
]

METRIC_LABELS = {
    "mem_max": "Memory Max (%)",
    "mem_avg": "Memory Avg Peak (%)",
    "cpu_avg": "CPU Avg Peak (%)",
    "net_in_avg": "NetworkIn Avg Peak (bytes)",
    "net_out_avg": "NetworkOut Avg Peak (bytes)",
    "energy_j": "Estimated Energy (J)",
    "avg_power_w": "Estimated Avg Power (W)",
}

INSTANCE_ORDER = ["java", "haskell"]


def build_queries(namespace, java_instance_id, haskell_instance_id, period):
    queries = []
    instances = {
        "java": java_instance_id,
        "haskell": haskell_instance_id,
    }

    for instance_name, instance_id in instances.items():
        for metric_id, metric_namespace, metric_name, stat in METRICS:
            effective_namespace = namespace if metric_namespace == "mestrado-etl" else metric_namespace
            queries.append(
                {
                    "Id": f"{instance_name}_{metric_id}",
                    "MetricStat": {
                        "Metric": {
                            "Namespace": effective_namespace,
                            "MetricName": metric_name,
                            "Dimensions": [
                                {"Name": "InstanceId", "Value": instance_id},
                            ],
                        },
                        "Period": period,
                        "Stat": stat,
                    },
                    "Label": f"{instance_name} {metric_id}",
                }
            )

    return queries


def run_aws_cli(region, start_time, end_time, queries):
    if shutil.which("aws") is None:
        raise RuntimeError("AWS CLI was not found in PATH.")

    cmd = [
        "aws",
        "cloudwatch",
        "get-metric-data",
        "--region",
        region,
        "--start-time",
        start_time,
        "--end-time",
        end_time,
        "--metric-data-queries",
        json.dumps(queries),
    ]

    completed = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        stderr = completed.stderr.strip() or "unknown AWS CLI error"
        raise RuntimeError(stderr)

    return json.loads(completed.stdout)


def parse_results(data):
    results = {
        instance: {metric_id: [] for metric_id, _, _, _ in METRICS}
        for instance in INSTANCE_ORDER
    }

    for item in data.get("MetricDataResults", []):
        result_id = item.get("Id", "")
        for instance in INSTANCE_ORDER:
            prefix = f"{instance}_"
            if result_id.startswith(prefix):
                metric_id = result_id[len(prefix):]
                if metric_id in results[instance]:
                    results[instance][metric_id] = item.get("Values", [])
                break

    return results


def estimate_energy(cpu_values, period, idle_watts, max_watts):
    if not cpu_values:
        return None, None

    watt_span = max_watts - idle_watts
    sample_powers = [
        idle_watts + (cpu_percent / 100.0) * watt_span
        for cpu_percent in cpu_values
    ]
    avg_power = mean(sample_powers)
    energy_j = sum(power * period for power in sample_powers)
    return energy_j, avg_power


def summarize(results, period, idle_watts, max_watts):
    summary = {}
    for instance in INSTANCE_ORDER:
        metrics = {}
        for metric_id, values in results[instance].items():
            metrics[metric_id] = max(values) if values else None

        energy_j, avg_power_w = estimate_energy(
            results[instance]["cpu_avg"],
            period,
            idle_watts,
            max_watts,
        )
        metrics["energy_j"] = energy_j
        metrics["avg_power_w"] = avg_power_w
        summary[instance] = metrics

    return summary


def format_value(value):
    if value is None:
        return "-"

    if abs(value) >= 1000:
        formatted = f"{value:,.0f}"
    else:
        formatted = f"{value:.2f}"

    return (
        formatted
        .replace(",", "__THOUSANDS__")
        .replace(".", ",")
        .replace("__THOUSANDS__", ".")
    )


def print_table(summary):
    headers = ["Metric", "Java", "Haskell"]
    rows = []
    ordered_metrics = [
        "mem_max",
        "mem_avg",
        "cpu_avg",
        "net_in_avg",
        "net_out_avg",
        "avg_power_w",
        "energy_j",
    ]

    for metric_id in ordered_metrics:
        rows.append(
            [
                METRIC_LABELS[metric_id],
                format_value(summary["java"][metric_id]),
                format_value(summary["haskell"][metric_id]),
            ]
        )

    all_rows = [headers, *rows]
    widths = [
        max(len(str(row[index])) for row in all_rows)
        for index in range(len(headers))
    ]

    def render(row):
        return " | ".join(str(value).ljust(widths[index]) for index, value in enumerate(row))

    print(render(headers))
    print("-+-".join("-" * width for width in widths))
    for row in rows:
        print(render(row))


def main():
    parser = argparse.ArgumentParser(
        description="Query CloudWatch metrics for both ETL instances and estimate energy spent during the interval."
    )
    parser.add_argument("--start-time", required=True, help="Interval start in ISO-8601, e.g. 2026-04-23T14:12:00Z")
    parser.add_argument("--end-time", required=True, help="Interval end in ISO-8601, e.g. 2026-04-23T14:16:00Z")
    parser.add_argument("--region", default=DEFAULT_REGION, help=f"AWS region. Default: {DEFAULT_REGION}")
    parser.add_argument("--namespace", default=DEFAULT_NAMESPACE, help=f"Custom CloudWatch namespace for memory metrics. Default: {DEFAULT_NAMESPACE}")
    parser.add_argument("--java-instance-id", default=DEFAULT_JAVA_INSTANCE_ID, help=f"Java EC2 instance ID. Default: {DEFAULT_JAVA_INSTANCE_ID}")
    parser.add_argument("--haskell-instance-id", default=DEFAULT_HASKELL_INSTANCE_ID, help=f"Haskell EC2 instance ID. Default: {DEFAULT_HASKELL_INSTANCE_ID}")
    parser.add_argument("--period", type=int, default=60, help="CloudWatch sampling period in seconds. Default: 60")
    parser.add_argument("--idle-watts", type=float, default=8.0, help="Estimated idle instance power draw in watts. Default: 8.0")
    parser.add_argument("--max-watts", type=float, default=20.0, help="Estimated max instance power draw in watts. Default: 20.0")
    args = parser.parse_args()

    if args.period <= 0:
        raise SystemExit("--period must be a positive integer.")
    if args.max_watts < args.idle_watts:
        raise SystemExit("--max-watts must be greater than or equal to --idle-watts.")

    try:
        data = run_aws_cli(
            args.region,
            args.start_time,
            args.end_time,
            build_queries(
                args.namespace,
                args.java_instance_id,
                args.haskell_instance_id,
                args.period,
            ),
        )
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1)

    summary = summarize(
        parse_results(data),
        args.period,
        args.idle_watts,
        args.max_watts,
    )
    print_table(summary)


if __name__ == "__main__":
    main()
