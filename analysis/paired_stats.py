from __future__ import annotations

import csv
import math
import re
from dataclasses import dataclass
from pathlib import Path
from statistics import mean, median


@dataclass(frozen=True)
class ExperimentRow:
    batch_size: int
    source_path: Path
    metrics: dict[str, tuple[float | None, float | None]]


def canonical_metric_label(label: str) -> str:
    if label.startswith("Gasto energético estimado"):
        return "Gasto energético estimado"
    return label


def parse_number(raw: str) -> float | None:
    value = raw.strip()
    if not value or value.upper() == "ERRO" or value == "-":
        return None

    if "," in value:
        value = value.replace(".", "").replace(",", ".")
    elif value.count(".") > 1:
        value = value.replace(".", "")

    try:
        return float(value)
    except ValueError:
        return None


def batch_size_from_path(path: Path) -> int:
    match = re.search(r"(\d+)", path.stem)
    if not match:
        raise ValueError(f"could not infer batch size from {path.name}")
    return int(match.group(1))


def load_experiment(path: Path) -> ExperimentRow:
    metrics: dict[str, tuple[float | None, float | None]] = {}
    batch_size = batch_size_from_path(path)

    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.reader(handle)
        for row in reader:
            if not row:
                continue
            label = row[0].strip()
            if label in {"", "Data", "Horário Início", "Horário fim", "Quantidade registros"}:
                continue
            if len(row) < 3:
                continue

            java = parse_number(row[1])
            haskell = parse_number(row[2])
            metrics[canonical_metric_label(label)] = (java, haskell)

    return ExperimentRow(batch_size=batch_size, source_path=path, metrics=metrics)


def load_experiments(results_dir: Path) -> list[ExperimentRow]:
    files = sorted(results_dir.glob("*.csv"), key=batch_size_from_path)
    return [load_experiment(path) for path in files]


def paired_values(
    experiments: list[ExperimentRow],
    metric_name: str,
) -> list[tuple[int, float, float]]:
    pairs: list[tuple[int, float, float]] = []
    for item in experiments:
        values = item.metrics.get(metric_name)
        if not values:
            continue
        java, haskell = values
        if java is None or haskell is None:
            continue
        pairs.append((item.batch_size, java, haskell))
    return pairs


def paired_differences(pairs: list[tuple[int, float, float]]) -> list[float]:
    return [java - haskell for _, java, haskell in pairs]


def paired_comparisons(pairs: list[tuple[int, float, float]]) -> list[dict[str, float]]:
    rows: list[dict[str, float]] = []
    for batch_size, java, haskell in pairs:
        diff = java - haskell
        abs_diff = abs(diff)
        pct_diff = (diff / haskell * 100.0) if haskell != 0 else math.nan
        ratio = (java / haskell) if haskell != 0 else math.nan
        rows.append(
            {
                "batch_size": batch_size,
                "java": java,
                "haskell": haskell,
                "diff": diff,
                "abs_diff": abs_diff,
                "pct_diff": pct_diff,
                "ratio": ratio,
            }
        )
    return rows


def descriptive_summary(diffs: list[float]) -> dict[str, float]:
    if not diffs:
        return {}

    if len(diffs) == 1:
        sd = 0.0
    else:
        mu = mean(diffs)
        sd = math.sqrt(sum((x - mu) ** 2 for x in diffs) / (len(diffs) - 1))

    return {
        "n": float(len(diffs)),
        "mean": mean(diffs),
        "median": median(diffs),
        "stdev": sd,
        "min": min(diffs),
        "max": max(diffs),
    }


def t_cdf(t_value: float, df: int) -> float:
    if df <= 0:
        raise ValueError("degrees of freedom must be positive")

    x = df / (df + t_value * t_value)
    prob = 0.5 * _betai(df / 2.0, 0.5, x)
    if t_value >= 0:
        return 1.0 - prob
    return prob


def paired_t_test(diffs: list[float]) -> dict[str, float]:
    n = len(diffs)
    if n < 2:
        return {"t": math.nan, "p": math.nan, "df": float(max(n - 1, 0))}

    mu = mean(diffs)
    sd = math.sqrt(sum((x - mu) ** 2 for x in diffs) / (n - 1))
    if sd == 0:
        return {"t": math.inf if mu != 0 else 0.0, "p": 0.0 if mu != 0 else 1.0, "df": float(n - 1)}

    t_value = mu / (sd / math.sqrt(n))
    p_value = 2.0 * min(t_cdf(t_value, n - 1), 1.0 - t_cdf(t_value, n - 1))
    return {"t": t_value, "p": p_value, "df": float(n - 1)}


def wilcoxon_signed_rank(diffs: list[float]) -> dict[str, float | str]:
    non_zero = [d for d in diffs if d != 0]
    n = len(non_zero)
    if n == 0:
        return {"w": 0.0, "p": 1.0, "method": "all differences are zero"}

    abs_values = sorted(abs(d) for d in non_zero)
    has_ties = any(abs_values[i] == abs_values[i - 1] for i in range(1, len(abs_values)))
    ranks = _rank_abs_values(non_zero)

    positive_sum = sum(rank for diff, rank in ranks if diff > 0)
    total_rank_sum = sum(rank for _, rank in ranks)
    w_stat = min(positive_sum, total_rank_sum - positive_sum)

    if has_ties:
        return {
            "w": w_stat,
            "p": _wilcoxon_normal_approx(ranks, positive_sum),
            "method": "normal approximation with tie correction",
        }

    distribution = {0.0: 1}
    for _, rank in ranks:
        next_distribution: dict[float, int] = {}
        for current_sum, count in distribution.items():
            next_distribution[current_sum] = next_distribution.get(current_sum, 0) + count
            new_sum = current_sum + rank
            next_distribution[new_sum] = next_distribution.get(new_sum, 0) + count
        distribution = next_distribution

    total_outcomes = 2 ** n
    tail = sum(count for signed_sum, count in distribution.items() if signed_sum <= w_stat)
    p_value = min(1.0, 2.0 * tail / total_outcomes)
    return {"w": w_stat, "p": p_value, "method": "exact"}


def _rank_abs_values(diffs: list[float]) -> list[tuple[float, float]]:
    ordered = sorted((abs(diff), diff) for diff in diffs if diff != 0)
    ranked: list[tuple[float, float]] = []
    index = 0
    while index < len(ordered):
        start = index
        value = ordered[index][0]
        while index < len(ordered) and ordered[index][0] == value:
            index += 1
        avg_rank = (start + 1 + index) / 2.0
        for _, diff in ordered[start:index]:
            ranked.append((diff, avg_rank))
    return ranked


def _wilcoxon_normal_approx(ranks: list[tuple[float, float]], positive_sum: float) -> float:
    n = len(ranks)
    total_rank = sum(rank for _, rank in ranks)
    mean_w = total_rank / 2.0
    variance_w = sum(rank * rank for _, rank in ranks) / 4.0
    if variance_w == 0:
        return 1.0
    z = (positive_sum - mean_w - 0.5 * math.copysign(1.0, positive_sum - mean_w)) / math.sqrt(variance_w)
    return math.erfc(abs(z) / math.sqrt(2.0))


def _betai(a: float, b: float, x: float) -> float:
    if x < 0.0 or x > 1.0:
        raise ValueError("x must be between 0 and 1")
    if x == 0.0 or x == 1.0:
        return float(x)

    ln_beta = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
    front = math.exp(math.log(x) * a + math.log(1.0 - x) * b + ln_beta)

    if x < (a + 1.0) / (a + b + 2.0):
        return front * _betacf(a, b, x) / a
    return 1.0 - front * _betacf(b, a, 1.0 - x) / b


def _betacf(a: float, b: float, x: float) -> float:
    max_iter = 200
    eps = 3.0e-7
    fpmin = 1.0e-30

    qab = a + b
    qap = a + 1.0
    qam = a - 1.0
    c = 1.0
    d = 1.0 - qab * x / qap
    if abs(d) < fpmin:
        d = fpmin
    d = 1.0 / d
    h = d

    for m in range(1, max_iter + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < fpmin:
            d = fpmin
        c = 1.0 + aa / c
        if abs(c) < fpmin:
            c = fpmin
        d = 1.0 / d
        h *= d * c

        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        if abs(d) < fpmin:
            d = fpmin
        c = 1.0 + aa / c
        if abs(c) < fpmin:
            c = fpmin
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < eps:
            break

    return h
