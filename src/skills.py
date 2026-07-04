"""
FS-1: Extract skills from posting descriptions using spaCy's PhraseMatcher
against a curated skills vocabulary, then aggregate frequency counts per
role category. This is the standard, production-realistic approach to
skill extraction (vs. generic NER, which doesn't reliably catch tool/tech
names like "Power BI" or "scikit-learn").
"""
import spacy
from spacy.matcher import PhraseMatcher
from collections import defaultdict, Counter
import pandas as pd

SKILL_VOCAB = [
    "SQL", "Excel", "Power BI", "Tableau", "Python", "pandas", "data visualization",
    "statistics", "A/B testing", "reporting", "data cleaning", "stakeholder communication",
    "machine learning", "scikit-learn", "feature engineering", "XGBoost", "deep learning",
    "experimentation", "ETL", "Airflow", "Spark", "AWS", "Docker", "data modeling",
    "PostgreSQL", "Redshift", "data pipelines", "Kafka", "PyTorch", "TensorFlow", "MLOps",
    "Kubernetes", "model deployment", "CI/CD", "requirements gathering", "Jira",
    "functional specifications", "process mapping", "UAT", "data validation", "Agile",
    "data profiling", "data governance", "data cleansing", "metadata management",
]

_nlp = None
_matcher = None


def _get_nlp():
    global _nlp, _matcher
    if _nlp is None:
        _nlp = spacy.load("en_core_web_sm", disable=["ner", "parser", "tagger", "lemmatizer"])
        _matcher = PhraseMatcher(_nlp.vocab, attr="LOWER")
        patterns = [_nlp.make_doc(skill) for skill in SKILL_VOCAB]
        _matcher.add("SKILLS", patterns)
    return _nlp, _matcher


def extract_skills(text: str) -> list:
    """Return the list of skill vocabulary terms found in a single text."""
    if not text:
        return []
    nlp, matcher = _get_nlp()
    doc = nlp(text)
    matches = matcher(doc)
    found = {doc[start:end].text for _, start, end in matches}
    # normalize casing back to canonical vocab form
    canon = {s.lower(): s for s in SKILL_VOCAB}
    return sorted({canon.get(f.lower(), f) for f in found})


def skill_frequency_by_category(df: pd.DataFrame) -> pd.DataFrame:
    """
    FS-1 acceptance criteria: top skills per role category with frequency counts.
    Returns a long-form DataFrame: category, skill, count.
    """
    counts = defaultdict(Counter)
    for _, row in df.iterrows():
        skills = extract_skills(row["description"])
        counts[row["category"]].update(skills)

    rows = []
    for category, counter in counts.items():
        for skill, count in counter.items():
            rows.append({"category": category, "skill": skill, "count": count})
    return pd.DataFrame(rows)


def top_skills_for_category(freq_df: pd.DataFrame, category: str, top_n: int = 10) -> pd.DataFrame:
    subset = freq_df[freq_df["category"] == category].sort_values("count", ascending=False)
    return subset.head(top_n)
