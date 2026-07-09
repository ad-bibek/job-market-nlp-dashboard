# Job Market Intelligence Dashboard — NLP Enhancement

A Streamlit dashboard that extends a global DS/AI job postings dataset with
NLP-driven features: skill extraction, topic clustering, and semantic
similarity search — built against a formal BRD and user story backlog
(see `docs/BRD.docx` if included alongside this project).

## What this demonstrates

This project pairs each engineering feature with the business requirement
it satisfies, mirroring how a Business/Data Analyst would scope and validate
a feature before (and after) it ships:

| User Story | Feature | Module |
|---|---|---|
| US-01 | Keyword search across postings | `app.py` (Search tab) |
| US-02 | Top skills per role category | `src/skills.py` |
| US-03 | Topic clustering across postings | `src/topics.py` |
| US-04 | Similar-posting recommendations | `src/similarity.py` |
| US-05 | Filterable summary dashboard | `app.py` (Overview tab) |
| US-06 | Data quality validation & logging | `src/validation.py` |

## Visual design

Styled as a "market terminal" — since this is literally job *market* intelligence,
the UI leans into that: dark ink background, an amber ticker strip surfacing live
stats under the title, monospace (IBM Plex Mono) for all data/metrics so figures
read like a trading-board readout, Space Grotesk for headings, Inter for body text.
Theme lives in `src/theme.py` (CSS) and `.streamlit/config.toml` (base Streamlit
theme tokens) — change the hex values in `src/theme.py`'s `:root` block to retheme.

## Setup

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
python data/generate_data.py     # regenerate the synthetic dataset (optional, already included)
streamlit run app.py
```

Then open the URL Streamlit prints (typically http://localhost:8501).

## Project structure

```
job_market_dashboard/
├── app.py                  # Streamlit UI — six tabs, one per user story
├── requirements.txt
├── .streamlit/
│   └── config.toml          # base theme tokens (dark, amber accent)
├── data/
│   ├── generate_data.py     # synthetic dataset generator (deterministic, seeded)
│   └── postings.csv         # 400 generated postings, ~6% intentionally malformed
└── src/
    ├── validation.py        # FS-4: required-field validation & exclusion log
    ├── skills.py             # FS-1: spaCy PhraseMatcher skill extraction
    ├── topics.py              # FS-2: TF-IDF + KMeans topic clustering, c-TF-IDF labeling
    ├── similarity.py          # FS-3: TF-IDF + SVD embeddings, cosine similarity search
    └── theme.py                # market-terminal CSS + ticker-strip component
```

## On the dataset

Real job-board scraping wasn't in scope here, so `data/generate_data.py`
generates a realistic synthetic dataset (six role categories, ten locations,
templated-but-varied descriptions, seeded for reproducibility) — including a
deliberate ~6% of malformed records so the data-quality validation feature
(US-06) has something real to catch. Swapping in a live-scraped or
Kaggle-sourced CSV with the same column schema (`posting_id, title, company,
category, location, seniority, description, posted_date`) requires no code
changes.

## On "BERTopic" and "embeddings"

The BRD specifies BERTopic and embedding-based similarity search. Both
typically run on sentence-transformer embeddings pulled from Hugging Face
Hub, which wasn't reachable in the build environment. `topics.py` and
`similarity.py` implement the same conceptual pipelines (vectorize → cluster
→ label; vectorize → nearest-neighbor by cosine similarity) using TF-IDF +
KMeans and TF-IDF + Truncated SVD (LSA) instead of a transformer backbone.
Both modules are isolated enough that swapping in real `bertopic` +
`sentence-transformers` later only touches `fit_topics()` and
`SimilarityIndex.__init__()` — nothing else in the app changes.

## Known limitations (be ready to discuss these)

- Synthetic data means skill/topic patterns are somewhat cleaner than
  real-world messy postings — worth mentioning if asked in an interview.
- Topic clustering was tuned to cluster on extracted skill profiles rather
  than raw description text, because raw-text clustering picked up shared
  template phrasing instead of real thematic signal. This is a real, honest
  design decision worth explaining, not something to hide.
