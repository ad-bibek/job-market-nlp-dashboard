"""
FS-3: Embedding-based similarity search between postings.

Same Hugging Face constraint as topics.py applies here: instead of
sentence-transformer embeddings, this builds dense semantic vectors via
TF-IDF + Truncated SVD (i.e., Latent Semantic Analysis), which is the
classical, well-established approach to dense document embeddings without
a transformer backbone. Cosine similarity over these vectors is used to
retrieve nearest postings, satisfying BR-3 / FS-3 as specified in the BRD.
"""
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity


class SimilarityIndex:
    def __init__(self, df: pd.DataFrame, n_components: int = 100):
        self.df = df.reset_index(drop=True)
        texts = self.df["description"].tolist()

        n_components = min(n_components, max(2, len(texts) - 1))
        self.vectorizer = TfidfVectorizer(stop_words="english", max_features=3000, min_df=2)
        X = self.vectorizer.fit_transform(texts)

        self.svd = TruncatedSVD(n_components=n_components, random_state=42)
        self.embeddings = self.svd.fit_transform(X)

    def similar_to(self, posting_id, top_n: int = 5) -> pd.DataFrame:
        idx_matches = self.df.index[self.df["posting_id"] == posting_id]
        if len(idx_matches) == 0:
            return pd.DataFrame()
        idx = idx_matches[0]

        sims = cosine_similarity(self.embeddings[idx].reshape(1, -1), self.embeddings).ravel()
        order = np.argsort(sims)[::-1]
        order = [i for i in order if i != idx][:top_n]

        result = self.df.iloc[order].copy()
        result["similarity"] = sims[order]
        return result.reset_index(drop=True)
