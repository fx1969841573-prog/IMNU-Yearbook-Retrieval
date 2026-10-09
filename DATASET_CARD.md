# Dataset Card

## Motivation and composition

This single-institution case study supports research on retrieval from Chinese university yearbooks, especially year and section cues. It contains 1,202 selectively de-identified knowledge units from 2014–2018, 60 queries, 2,209 graded judgments, and 19 frozen Top 10 runs. The repository also contains the paper's final aggregate, per-query, ablation, sensitivity, and significance results.

## Construction and query design

The corpus was segmented into knowledge units with stable `chunk_id`, year, and structural fields. The 60 designed queries cover single-year facts (16), cross-year comparison (6), structural location (22), and semantic summarization (16). Query text has not been rewritten for this release. The Top 10 rankings are frozen outputs of the paper experiments; the public text was prepared later and is not their input.

## Relevance annotation and quality control

Each qrel judges one query–unit pair with a label of 0, 1, or 2. Label 0 is not useful, label 1 supplies partial or supporting evidence, and label 2 supplies a core fact, answer item, structural location, or key evidence. The final 2,209 pairs have distribution 766 / 323 / 1,120. Their labels were reviewed under one three-level guideline. A second annotator independently blind-labeled 180 items; 134 agreed (74.44% raw agreement), with unweighted Cohen's κ = 0.6032. All 46 disagreements were manually adjudicated. Only the 180-item subset received this independent second annotation.

The judgments are pooled and incomplete outside the evaluated candidate set. An absent pair must be treated as unjudged. The 19 Top 10 runs contain 1,992 unique pairs and every ranked pair is judged.

## Anonymization

The corpus applies targeted de-identification to direct source-institution identifiers, unnecessary internal identifiers, and sensitive personal information. Publicly documented ordinary names, college names, awards, appointments, and activities are not universally removed. No claim of complete anonymity or zero re-identification risk is made. The source institution is disclosed in the manuscript.

## Intended use and out-of-scope use

The frozen runs plus qrels support static verification of the paper's retrieval metrics without model execution. The de-identified corpus can support new retrieval studies if investigators state the effect of text changes and choose an explicit protocol for unjudged results. The data should not be used to infer sensitive attributes or claim that the judgments cover all possible results. Retrieval scores here do not measure generated-answer quality.

## Limitations

Coverage is one institution, five years, and 60 constructed queries. Pooled qrels are not exhaustive. The public text differs from the frozen experimental text; a known `q28` query–unit semantic consistency limitation is documented in the release notes. Repeating retrieval on the public text is not guaranteed to reproduce frozen ranks.

## Access and licensing

Files under `data/` and dataset-derived benchmark materials are available
for academic and scientific research use under
[DATA_USE_TERMS.md](DATA_USE_TERMS.md). These research-use terms are not
an MIT License or an unrestricted open-data license.

Original project code under `scripts/` is licensed under the MIT License;
see [scripts/LICENSE](scripts/LICENSE). The MIT License does not apply to
the dataset, corpus, queries, qrels, or benchmark data.

Commercial use, independent republication of the corpus as a separate
dataset, and intentional re-identification are not permitted without
separate authorization. Viewing, downloading, cloning, and forking the
official public repository for permitted research use are allowed under
the research-use terms.

Rights in the underlying yearbook materials remain with the applicable
rights holders. These terms apply only to rights the maintainers are
authorized to grant and do not override underlying source rights.
