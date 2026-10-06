
from pathlib import Path
import os

import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer


# Keep the vectorizer beside the persistent ChromaDB data.
DATA_DIR = Path(__file__).resolve().parent.parent / "chroma_data"
VECTORIZER_PATH = DATA_DIR / "tfidf_vectorizer.joblib"


def fit_vectorizer(texts: list[str]):
    """Fit one TF-IDF vocabulary and return it with the corpus vectors."""
    valid_texts = [
        text for text in texts
        if isinstance(text, str) and text.strip()
    ]

    if not valid_texts:
        raise ValueError("Cannot fit TF-IDF on empty text.")

    vectorizer = TfidfVectorizer(
        lowercase=True,
        stop_words="english",
        ngram_range=(1, 2),
        dtype=np.float64
    )

    try:
        matrix = vectorizer.fit_transform(valid_texts)
    except ValueError as error:
        raise ValueError("TF-IDF could not build a vocabulary from the text.") from error

    return vectorizer, matrix


def save_vectorizer(vectorizer, version: str) -> Path:
    """Atomically persist a vectorizer tied to a collection generation."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = DATA_DIR / f"tfidf_vectorizer_{version}.joblib"
    temporary_path = path.with_suffix(path.suffix + ".tmp")
    joblib.dump(vectorizer, temporary_path)
    os.replace(temporary_path, path)
    return path


def delete_vectorizer(version: str) -> None:
    path = DATA_DIR / f"tfidf_vectorizer_{version}.joblib"
    path.unlink(missing_ok=True)


def fit_embeddings(texts: list[str]):
    """Fit TF-IDF, persist the legacy vectorizer path, and return its vectors."""
    vectorizer, matrix = fit_vectorizer(texts)

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(vectorizer, VECTORIZER_PATH)

    return matrix


def load_vectorizer(version: str | None = None):
    """Load a collection's vocabulary, or the legacy vectorizer by default."""
    path = (
        DATA_DIR / f"tfidf_vectorizer_{version}.joblib"
        if version
        else VECTORIZER_PATH
    )

    if not path.exists():
        raise FileNotFoundError(
            "No fitted TF-IDF vectorizer found. Index a website first."
        )

    return joblib.load(path)


def embed_query(query: str, vectorizer_version: str | None = None):
    """Transform a query using the saved document vocabulary."""
    if not query or not query.strip():
        raise ValueError("Query cannot be empty.")

    vectorizer = load_vectorizer(vectorizer_version)
    return vectorizer.transform([query.strip()])
