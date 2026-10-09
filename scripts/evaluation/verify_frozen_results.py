"""Verify frozen rankings, relevance judgments, metrics, and significance tests.

This script reads the published inputs only. It never reruns retrieval or writes files.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

from scipy.stats import wilcoxon
from statsmodels.stats.multitest import multipletests


ROOT = Path(__file__).resolve().parents[2]
METRICS = ("P@10", "R@10", "MRR@10", "nDCG@10", "Hit@10")
QRELS_SHA256 = "bd87e2885715e32e7f535b793965e593289358379969f79a5c99ad8aa6012c46"
RUN_NAMES = {
    "BM25": "BM25",
    "Structure-aware BM25": "SA-BM25",
    "bge-small (plain)": "BGE-small plain",
    "bge-small (structure-aware)": "BGE-small SA",
    "bge-large (plain)": "BGE-large plain",
    "bge-large (structure-aware)": "BGE-large SA",
    "text2vec (plain)": "text2vec plain",
    "text2vec (structure-aware)": "text2vec SA",
    **{f"Hybrid alpha={a}": f"Hybrid alpha={a}" for a in ("0.0", "0.2", "0.4", "0.5", "0.6", "0.8", "1.0")},
    "SA-BM25 ablation: no year filter": "no_year_filter",
    "SA-BM25 ablation: no structure index": "no_structure_index",
    "SA-BM25 ablation: no structure bonus": "no_structure_bonus",
    "SA-BM25 ablation: no explicit catalog filter": "no_explicit_catalog_filter",
}


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def check_close(actual: float, expected: str, where: str, digits: int = 10) -> None:
    if f"{actual:.{digits}f}" != f"{float(expected):.{digits}f}":
        raise ValueError(f"{where}: {actual} != {expected}")


def load_inputs():
    queries = json.loads((ROOT / "data/queries/queries.json").read_text(encoding="utf-8-sig"))
    ids = {q["query_id"] for q in queries}
    assert len(queries) == len(ids) == 60
    assert Counter(q["query_type"] for q in queries) == {
        "single_year_fact": 16, "cross_year_comparison": 6,
        "structure_locating": 22, "semantic_summary": 16,
    }
    assert all(set(q) == {"query_id", "query", "query_type"} for q in queries)

    qrels_path = ROOT / "data/qrels/qrels.csv"
    assert hashlib.sha256(qrels_path.read_bytes()).hexdigest() == QRELS_SHA256
    fields, rows = read_csv(qrels_path)
    assert fields == ["query_id", "chunk_id", "label"] and len(rows) == 2209
    qrels = {}
    by_query = defaultdict(list)
    for row in rows:
        pair = row["query_id"], row["chunk_id"]
        if pair in qrels or pair[0] not in ids or row["label"] not in {"0", "1", "2"}:
            raise ValueError(f"invalid qrel {pair}")
        qrels[pair] = int(row["label"])
        by_query[pair[0]].append(qrels[pair])
    assert Counter(qrels.values()) == {0: 766, 1: 323, 2: 1120}

    files = sorted((ROOT / "benchmark/top10").glob("*_top10.csv"))
    assert len(files) == 19
    runs = {}
    union = set()
    for path in files:
        fields, rows = read_csv(path)
        assert fields == ["method", "query_id", "chunk_id", "rank", "score"]
        assert len(rows) == 600
        names = {row["method"] for row in rows}
        assert len(names) == 1
        name = RUN_NAMES[names.pop()]
        if name in runs:
            raise ValueError(f"duplicate run {name}")
        grouped = defaultdict(dict)
        for row in rows:
            pair = row["query_id"], row["chunk_id"]
            if pair not in qrels:
                raise ValueError(f"unjudged Top 10 pair {pair}")
            rank = int(row["rank"])
            float(row["score"])
            if rank in grouped[pair[0]]:
                raise ValueError(f"duplicate rank {name}/{pair[0]}/{rank}")
            grouped[pair[0]][rank] = pair[1]
            union.add(pair)
        assert set(grouped) == ids
        assert all(set(ranks) == set(range(1, 11)) and len(set(ranks.values())) == 10
                   for ranks in grouped.values())
        runs[name] = grouped
    assert set(runs) == set(RUN_NAMES.values()) and len(union) == 1992
    return ids, qrels, by_query, runs


def calculate(ids, qrels, by_query, runs):
    per_query = {}
    summary = {}
    for method, run in runs.items():
        for qid in sorted(ids):
            labels = [qrels[(qid, run[qid][rank])] for rank in range(1, 11)]
            relevant = sum(value >= 1 for value in labels)
            total_relevant = sum(value >= 1 for value in by_query[qid])
            first = next((rank for rank, value in enumerate(labels, 1) if value >= 1), None)
            dcg = sum(value / math.log2(rank + 1) for rank, value in enumerate(labels, 1))
            ideal = sorted(by_query[qid], reverse=True)[:10]
            idcg = sum(value / math.log2(rank + 1) for rank, value in enumerate(ideal, 1))
            per_query[method, qid] = {
                "P@10": relevant / 10,
                "R@10": relevant / total_relevant if total_relevant else 0.0,
                "MRR@10": 1 / first if first else 0.0,
                "nDCG@10": dcg / idcg if idcg else 0.0,
                "Hit@10": float(relevant > 0),
            }
        summary[method] = {
            metric: sum(per_query[method, qid][metric] for qid in ids) / 60
            for metric in METRICS
        }
    return per_query, summary


def verify_tables(ids, per_query, summary):
    _, rows = read_csv(ROOT / "benchmark/per_query_metrics.csv")
    expected = {(row["method"], row["query_id"]): row for row in rows}
    assert len(rows) == len(expected) == 1140
    assert set(expected) == set(per_query)
    for key, scores in per_query.items():
        for metric in METRICS:
            check_close(scores[metric], expected[key][metric], f"per query {key}/{metric}")

    for filename, get_method in (
        ("main_results.csv", lambda row: row["method"]),
        ("ablation_results.csv", lambda row: "SA-BM25" if row["method"] == "SA-BM25 full" else row["method"]),
        ("hybrid_sensitivity.csv", lambda row: f"Hybrid alpha={row['alpha']}"),
    ):
        _, rows = read_csv(ROOT / "benchmark" / filename)
        for row in rows:
            method = get_method(row)
            for metric in METRICS:
                check_close(summary[method][metric], row[metric], f"{filename}/{method}/{metric}")


def verify_significance(ids, per_query):
    _, rows = read_csv(ROOT / "benchmark/significance_tests.csv")
    expected = {row["metric"]: row for row in rows}
    assert len(rows) == len(expected) == 4
    p_values = []
    calculated = []
    for metric in METRICS[:4]:
        sa = [float(f"{per_query['SA-BM25', qid][metric]:.10f}") for qid in sorted(ids)]
        bm = [float(f"{per_query['BM25', qid][metric]:.10f}") for qid in sorted(ids)]
        diffs = [x - y for x, y in zip(sa, bm)]
        result = wilcoxon(sa, bm, alternative="two-sided", zero_method="wilcox",
                          correction=False, method="auto")
        p_values.append(float(result.pvalue))
        calculated.append((metric, sa, bm, diffs, result))
    rejected, adjusted, _, _ = multipletests(p_values, alpha=0.05, method="holm")
    for (metric, sa, bm, diffs, result), decision, holm_p in zip(calculated, rejected, adjusted):
        row = expected[metric]
        for field, value in (
            ("sa_bm25_mean", sum(sa) / 60), ("bm25_mean", sum(bm) / 60),
            ("mean_difference", sum(diffs) / 60),
            ("wilcoxon_statistic", result.statistic), ("raw_p", result.pvalue),
            ("holm_adjusted_p", holm_p),
        ):
            if not math.isclose(float(value), float(row[field]), rel_tol=0, abs_tol=5e-10):
                raise ValueError(f"significance {metric}/{field}")
        for field, count in (
            ("nonzero_difference_count", sum(x != 0 for x in diffs)),
            ("zero_difference_count", sum(x == 0 for x in diffs)),
            ("positive_difference_count", sum(x > 0 for x in diffs)),
            ("negative_difference_count", sum(x < 0 for x in diffs)),
        ):
            assert int(row[field]) == count, (metric, field)
        assert row["significant"] == ("yes" if decision else "no")


def main():
    ids, qrels, by_query, runs = load_inputs()
    per_query, summary = calculate(ids, qrels, by_query, runs)
    verify_tables(ids, per_query, summary)
    verify_significance(ids, per_query)
    print("PASS: corpus-independent verification of 60 queries, 2209 qrels, 19 frozen Top 10 runs")
    print("PASS: five metrics, 1140 per-query rows, four Wilcoxon tests with Holm correction")
    print("BM25:", *(f"{summary['BM25'][metric]:.4f}" for metric in METRICS))
    print("SA-BM25:", *(f"{summary['SA-BM25'][metric]:.4f}" for metric in METRICS))


if __name__ == "__main__":
    main()
