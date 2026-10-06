import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import chromadb
import services.embedding_service as embedding_service
import services.vector_store as vector_store

class VectorSearchTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.client = chromadb.EphemeralClient()
        self.client_patch = patch.object(vector_store, "client", self.client)
        self.client_patch.start()

        self.collection_name = f"learnloom_test_{id(self)}"
        self.name_patch = patch.object(
            vector_store,
            "COLLECTION_NAME",
            self.collection_name,
        )
        self.name_patch.start()
        initial_collection = self.client.create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        self.collection = initial_collection
        self.collection_patch = patch.object(
            vector_store,
            "collection",
            initial_collection,
        )
        self.collection_patch.start()

        data_dir = Path(self.temp_dir.name) / "vectors"
        self.data_dir_patch = patch.object(
            embedding_service,
            "DATA_DIR",
            data_dir,
        )
        self.data_dir_patch.start()
        self.path_patch = patch.object(
            embedding_service,
            "VECTORIZER_PATH",
            data_dir / "tfidf_vectorizer.joblib",
        )
        self.path_patch.start()

    def tearDown(self):
        self.path_patch.stop()
        self.data_dir_patch.stop()
        self.collection_patch.stop()
        self.name_patch.stop()
        self.client_patch.stop()
        self.temp_dir.cleanup()

    def test_reindexing_same_url_replaces_chunks_without_duplicates(self):
        url = "https://one.example.org/guide"
        first = [
            {"chunk_id": 0, "section_title": "Start", "text": "learn basic concepts"},
            {"chunk_id": 1, "section_title": "Next", "text": "practice useful examples"},
        ]
        replacement = [
            {"chunk_id": 0, "section_title": "Updated", "text": "review updated concepts"},
        ]

        self.assertEqual(vector_store.index_chunks(url, first), 2)
        self.assertEqual(vector_store.collection.count(), 2)
        self.assertEqual(vector_store.index_chunks(url, replacement), 1)
        self.assertEqual(vector_store.collection.count(), 1)

    def test_rebuild_changes_dimension_and_preserves_other_websites(self):
        archived_url = "https://archive.example.org/page"
        self.collection.add(
            ids=["legacy-archive-record"],
            documents=["archived research records"],
            metadatas=[{
                "source_url": archived_url,
                "section_title": "Archive",
                "chunk_id": 0,
            }],
            embeddings=[[0.1] * 52],
        )

        terms = " ".join(f"concept{index}marker" for index in range(70))
        new_url = "https://new.example.org/page"
        vector_store.index_chunks(
            new_url,
            [{"chunk_id": 0, "section_title": "Concepts", "text": terms}],
        )

        records = vector_store.collection.get(
            where={"source_url": archived_url},
            include=["documents", "embeddings"],
        )
        self.assertEqual(records["documents"], ["archived research records"])
        self.assertNotEqual(len(records["embeddings"][0]), 52)
        self.assertEqual(vector_store.collection.count(), 2)

        archived_results = vector_store.search_chunks(
            "archived research",
            source_url=archived_url,
        )
        self.assertEqual(len(archived_results), 1)
        self.assertEqual(archived_results[0]["source_url"], archived_url)

    def test_url_filter_and_question_change_retrieved_section(self):
        url = "https://garden.example.org/guide"
        other_url = "https://database.example.org/guide"
        vector_store.index_chunks(url, [
            {"chunk_id": 0, "section_title": "Orchards", "text": "apple orchards need seasonal pruning"},
            {"chunk_id": 1, "section_title": "Pollination", "text": "bees pollinate flowers across gardens"},
        ])
        vector_store.index_chunks(other_url, [
            {"chunk_id": 0, "section_title": "Indexes", "text": "database indexes speed up query lookups"},
        ])

        pruning_results = vector_store.search_chunks(
            "orchard pruning",
            source_url=url,
        )
        pollination_results = vector_store.search_chunks(
            "bee pollination flowers",
            source_url=url,
        )
        wrong_site_results = vector_store.search_chunks(
            "orchard pruning",
            source_url=other_url,
        )

        self.assertEqual(pruning_results[0]["section_title"], "Orchards")
        self.assertEqual(pollination_results[0]["section_title"], "Pollination")
        self.assertTrue(all(item["source_url"] == url for item in pruning_results))
        self.assertTrue(all(item["source_url"] == url for item in pollination_results))
        self.assertEqual(wrong_site_results, [])

    def test_empty_content_and_empty_vocabulary_are_reported(self):
        with self.assertRaisesRegex(ValueError, "No valid text chunks"):
            vector_store.index_chunks("https://empty.example.org", [])

        with self.assertRaisesRegex(ValueError, "could not build a vocabulary"):
            vector_store.index_chunks(
                "https://stopwords.example.org",
                [{"chunk_id": 0, "text": "the and or"}],
            )

        self.assertEqual(vector_store.collection.count(), 0)

    def test_search_requires_a_website_url(self):
        with self.assertRaisesRegex(ValueError, "Source URL is required"):
            vector_store.search_chunks("some question", source_url="")


if __name__ == "__main__":
    unittest.main()