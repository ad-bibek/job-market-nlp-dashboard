"""
FS-2: Group postings into thematic topic clusters.

Note on implementation: BERTopic's default pipeline uses sentence-transformer
embeddings pulled from Hugging Face. This environment doesn't have Hugging Face
Hub access, so this module implements the same conceptual pipeline BERTopic
uses -- vectorize -> cluster -> label clusters with class-based TF-IDF (c-TF-IDF)
-- using scikit-learn's TF-IDF + KMeans instead of a transformer backbone.
Swapping in `bertopic` + `sentence-transformers` later is a drop-in upgrade:
only `fit_topics()` below would need to change.
"""
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

STOPWORD_EXTRAS = {"experience", "team", "role", "join", "candidate", "candidates",
                   "looking", "working", "opportunity", "responsibilities", "required",
                   "bonus points", "bonus", "proficient", "ll", "core", "practical",
                   "preferred", "requirements include", "cross", "cross functional",
                   "business decisions", "growing team", "fast", "paced"}


def fit_topics(df: pd.DataFrame, n_topics: int = 6, random_state: int = 42, text_col: str = "description"):
    """
    Returns (df_with_topics, topic_labels_dict).
    df_with_topics adds a `topic_id` column.
    topic_labels_dict maps topic_id -> human-readable label (top c-TF-IDF terms).

    text_col: which column to cluster on. Defaults to full description text;
    pass a skill-based text column for topics that read as skill clusters
    rather than generic phrasing clusters.
    """
    texts = df[text_col].tolist()

    vectorizer = TfidfVectorizer(
        stop_words="english", max_features=3000, ngram_range=(1, 2), min_df=2, max_df=0.35
    )
    X = vectorizer.fit_transform(texts)

    n_topics = min(n_topics, max(2, len(df) // 20))
    km = KMeans(n_clusters=n_topics, random_state=random_state, n_init=10)
    labels = km.fit_predict(X)

    out = df.copy()
    out["topic_id"] = labels

    # c-TF-IDF style labeling: for each cluster, find terms most distinctive
    # to that cluster relative to all other clusters combined.
    vocab = np.array(vectorizer.get_feature_names_out())
    topic_labels = {}
    for t in range(n_topics):
        mask = labels == t
        if mask.sum() == 0:
            topic_labels[t] = "Empty"
            continue
        cluster_mean = np.asarray(X[mask].mean(axis=0)).ravel()
        other_mean = np.asarray(X[~mask].mean(axis=0)).ravel() if (~mask).sum() else np.zeros_like(cluster_mean)
        distinctiveness = cluster_mean - other_mean
        top_idx = distinctiveness.argsort()[::-1][:4]
        terms = [vocab[i] for i in top_idx if vocab[i] not in STOPWORD_EXTRAS]
        topic_labels[t] = ", ".join(terms[:3]) if terms else f"Topic {t}"

    return out, topic_labels
