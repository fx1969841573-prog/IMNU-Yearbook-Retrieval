# IMNU-Yearbook Retrieval Dataset

This dataset is a structure-aware retrieval benchmark built from five annual university yearbooks (2014–2018). It is a single-institution case study with 1,202 knowledge units, 60 queries, and 2,209 judged query–unit pairs. The text in this repository has been selectively de-identified. The paper discloses the source institution.

## Task and data

Each query retrieves knowledge units using their text and yearbook structure. `data/corpus/corpus_anonymized.jsonl` contains `chunk_id`, `year`, `section_level`, `section_path`, and `text`. `data/queries/queries.json` contains `query_id`, `query`, and `query_type`. `data/qrels/qrels.csv` contains `query_id`, `chunk_id`, and `label`.

| Item | Count |
|---|---:|
| Knowledge units | 1,202 |
| Queries | 60 |
| Judged pairs | 2,209 |
| Labels 0 / 1 / 2 | 766 / 323 / 1,120 |
| Frozen Top 10 runs | 19 × 600 = 11,400 rows |
| Unique pairs in the Top 10 pool | 1,992 |

Query types: `single_year_fact` 16, `cross_year_comparison` 6, `structure_locating` 22, and `semantic_summary` 16.

Label 0 means the unit does not materially help answer the query; label 1 means partial answer, background, or supporting evidence; label 2 means a core fact, valid answer item, target structural location, or key evidence. A label 2 unit need not answer a complex query by itself. A pair absent from qrels is **unjudged**, not label 0.

All 2,209 judgments underwent a unified manual review. A second annotator independently and blindly labeled 180 items: raw agreement was 74.44%, and unweighted Cohen's κ was 0.6032. All 46 disagreements were manually adjudicated. This does not imply independent double annotation of all 2,209 items.

## Files and benchmark

```text
data/corpus/corpus_anonymized.jsonl
data/queries/queries.json
data/qrels/qrels.csv
benchmark/top10/                 # 19 text-free frozen rankings
benchmark/main_results.csv       # eight main methods
benchmark/ablation_results.csv   # five structural configurations
benchmark/hybrid_sensitivity.csv # seven fixed weights
benchmark/significance_tests.csv # paired Wilcoxon and Holm
benchmark/per_query_metrics.csv
scripts/evaluation/verify_frozen_results.py
checksums/SHA256SUMS.txt
docs/RELEASE_NOTES.md
```

The frozen Top 10 files contain `method`, `query_id`, `chunk_id`, `rank`, and `score`. Structure-aware BM25 (SA-BM25) is a structure-utilizing baseline, not a newly proposed ranking algorithm.

Final qrels SHA-256: `bd87e2885715e32e7f535b793965e593289358379969f79a5c99ad8aa6012c46`.

## Reproduce the reported evaluation

From the repository root:

```sh
python -m pip install -r scripts/evaluation/requirements.txt
python scripts/evaluation/verify_frozen_results.py
```

The read-only script uses the queries, final qrels, and existing Top 10 rankings to recompute P@10, R@10, MRR@10, nDCG@10, Hit@10, and four two-sided paired Wilcoxon tests with Holm correction for SA-BM25 versus BM25. It requires no retrieval models. Binary relevance uses label ≥ 1; nDCG uses the 0/1/2 labels as linear gains. Metrics are macro-averaged across 60 queries. Unjudged ranked items cause an error.

The public corpus differs in text from the corpus used to generate the frozen rankings, so rerunning retrieval on public text need not reproduce those rankings. One known `q28` query–unit semantic consistency limitation remains after de-identification. The frozen judgment is retained for paper reproducibility; when evaluating a new method on public text, handle that pair explicitly and do not treat pool-external unjudged items as label 0. See [release notes](docs/RELEASE_NOTES.md).

## Privacy, scope, and access

The public corpus selectively generalizes the source institution's direct identifiers, internal identifying details, and sensitive personal information. Ordinary public facts, college names, and names are not universally removed. This is not complete anonymity and does not eliminate re-identification risk.

The benchmark covers one institution, five years, and 60 designed queries. Pooled judgments are not exhaustive over all possible retrieved units. No original PDF, unredacted text, internal annotation workbook, local model, or cache is included.

## License and Data Use

### Dataset

Files under `data/` and dataset-derived benchmark materials are
provided for academic and scientific research use subject to
[DATA_USE_TERMS.md](DATA_USE_TERMS.md).

These terms do not constitute an unrestricted open-data license.
Commercial use and independent redistribution of the corpus are not
authorized unless separate permission is obtained.

### Code

Original project code under `scripts/` is licensed under the MIT
License. See [scripts/LICENSE](scripts/LICENSE).

The MIT License does **not** apply to the dataset, corpus text,
qrels, queries, benchmark data, or underlying yearbook materials.

## Citation

Manuscript: *高校年鉴结构感知检索数据集构建与评测* (under submission). Formal publication details are pending; see `CITATION.cff`.
