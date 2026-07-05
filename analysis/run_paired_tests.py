#!/usr/bin/env python3
from __future__ import annotations

import csv
import argparse
from pathlib import Path

from paired_stats import (
    descriptive_summary,
    load_experiments,
    paired_comparisons,
    paired_differences,
    paired_t_test,
    paired_values,
    wilcoxon_signed_rank,
)


DEFAULT_METRICS = [
    "Tempo (ms)",
    "Pico Memória (%)",
    "Pico CPU (%)",
    "Entrada de rede (bytes)",
    "Saída de rede (bytes)",
    "Gasto energético estimado",
]


def format_float(value: float | None) -> str:
    if value is None:
        return "-"
    if value != value:
        return "nan"
    return f"{value:.6f}"


def write_summary_csv(path: Path, rows: list[dict[str, object]]) -> None:
    fieldnames = [
        "metric",
        "paired_n",
        "mean_diff",
        "median_diff",
        "stdev",
        "min",
        "max",
        "paired_t_t",
        "paired_t_df",
        "paired_t_p",
        "wilcoxon_w",
        "wilcoxon_p",
        "wilcoxon_method",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_pairs_csv(path: Path, rows: list[dict[str, object]]) -> None:
    fieldnames = ["metric", "batch_size", "java", "haskell", "diff", "abs_diff", "pct_diff", "ratio"]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def pick_metric_name(experiments, requested: str) -> str | None:
    available = {metric for exp in experiments for metric in exp.metrics}
    if requested in available:
        return requested

    aliases = {
        "Gasto energético estimado": ["Gasto energético estimado"],
    }
    for candidate in aliases.get(requested, [requested]):
        if candidate in available:
            return candidate
    return None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run paired statistical tests over the experiment result CSVs."
    )
    parser.add_argument(
        "--results-dir",
        default="results",
        help="Directory containing the experiment CSV files.",
    )
    parser.add_argument(
        "--metric",
        action="append",
        dest="metrics",
        help="Metric label to analyze. Repeat to limit output. Defaults to the main comparable metrics.",
    )
    args = parser.parse_args()

    results_dir = Path(args.results_dir)
    experiments = load_experiments(results_dir)
    if not experiments:
        print(f"No CSV files found in {results_dir}")
        return 1

    requested_metrics = args.metrics or DEFAULT_METRICS
    metrics_to_analyze: list[str] = []
    for metric in requested_metrics:
        resolved = pick_metric_name(experiments, metric)
        if resolved and resolved not in metrics_to_analyze:
            metrics_to_analyze.append(resolved)

    if not metrics_to_analyze:
        print("No matching metrics found in the results CSV files.")
        return 1

    print(f"Results directory: {results_dir}")
    print(f"Experiments loaded: {len(experiments)}")
    print()

    summary_rows: list[dict[str, object]] = []
    pair_rows: list[dict[str, object]] = []

    for metric_name in metrics_to_analyze:
        pairs = paired_values(experiments, metric_name)
        diffs = paired_differences(pairs)
        comparisons = paired_comparisons(pairs)
        for row in comparisons:
            pair_rows.append({"metric": metric_name, **row})

        print(f"Metric: {metric_name}")
        print(f"Paired samples: {len(diffs)}")
        if not diffs:
            print("Status: no comparable Java/Haskell values found")
            print()
            continue

        summary = descriptive_summary(diffs)
        t_result = paired_t_test(diffs)
        w_result = wilcoxon_signed_rank(diffs)

        summary_rows.append(
            {
                "metric": metric_name,
                "paired_n": len(diffs),
                "mean_diff": summary.get("mean"),
                "median_diff": summary.get("median"),
                "stdev": summary.get("stdev"),
                "min": summary.get("min"),
                "max": summary.get("max"),
                "paired_t_t": t_result["t"],
                "paired_t_df": t_result["df"],
                "paired_t_p": t_result["p"],
                "wilcoxon_w": w_result["w"],
                "wilcoxon_p": w_result["p"],
                "wilcoxon_method": w_result["method"],
            }
        )

        print(f"Mean difference (Java - Haskell): {format_float(summary.get('mean'))}")
        print(f"Median difference: {format_float(summary.get('median'))}")
        print(f"Std. deviation: {format_float(summary.get('stdev'))}")
        print(f"Min / Max: {format_float(summary.get('min'))} / {format_float(summary.get('max'))}")
        print(
            "Paired t-test: "
            f"t={format_float(t_result['t'])}, df={format_float(t_result['df'])}, p={format_float(t_result['p'])}"
        )
        print(
            "Wilcoxon signed-rank: "
            f"W={format_float(w_result['w'])}, p={format_float(w_result['p'])}, method={w_result['method']}"
        )
        print("Pairs:")
        for batch_size, java, haskell in pairs:
            diff = java - haskell
            abs_diff = abs(diff)
            pct_diff = (diff / haskell * 100.0) if haskell != 0 else float("nan")
            ratio = (java / haskell) if haskell != 0 else float("nan")
            print(
                f"  batch={batch_size}: java={java:.6f}, haskell={haskell:.6f}, diff={diff:.6f}, "
                f"abs_diff={abs_diff:.6f}, pct_diff={pct_diff:.6f}, ratio={ratio:.6f}"
            )
        print()

    summary_csv = results_dir / "paired_tests_summary.csv"
    pairs_csv = results_dir / "paired_tests_pairs.csv"
    write_summary_csv(summary_csv, summary_rows)
    write_pairs_csv(pairs_csv, pair_rows)
    print(f"Saved summary CSV: {summary_csv}")
    print(f"Saved pairs CSV: {pairs_csv}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
