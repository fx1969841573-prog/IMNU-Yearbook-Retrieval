# Release notes — v1.0.0 public research release

This release contains a selectively de-identified corpus of 1,202 knowledge units, 60 unchanged public queries, and the final frozen 2,209 qrels (labels 0/1/2: 766/323/1,120). It includes 19 frozen Top 10 configurations, each with 60 queries × 10 ranks: 11,400 rows and 1,992 unique candidate pairs.

The final qrels underwent a unified manual review. A second annotator independently blind-labeled 180 items (134 agreements; 74.44% raw agreement; unweighted Cohen's κ 0.6032), and all 46 disagreements were adjudicated. Historical intermediate annotation artifacts are not part of this release.

This package also includes the final eight-method main results, five structural configurations, seven fixed hybrid weights, per-query metrics, and paired Wilcoxon results with four-test Holm correction. The evaluation script recomputes these from the frozen rankings and qrels; no retrieval model execution is required.

**Known public-text limitation:** one `q28` query–unit pair has a semantic consistency difference between the de-identified text and the frozen evaluation text. The frozen qrel is retained to reproduce the paper's evaluation. Treat this pair explicitly in new evaluations on the public text. Pool-external results are unjudged and cannot automatically be assigned label 0.

The corpus is selectively de-identified, not guaranteed anonymous. Original PDFs, unredacted experimental text, historical annotation workbooks, local paths, caches, and model files are excluded. This release is available for academic and scientific research use under DATA_USE_TERMS.md.

Before the v1.0.0 public release, additional targeted anonymization
was applied to person–sensitive-information associations identified
during the final privacy audit. Chunk identifiers and frozen benchmark
judgments were unchanged.

Data access: Research use only; see DATA_USE_TERMS.md.

Code: MIT License for original project code under scripts/; see scripts/LICENSE.
