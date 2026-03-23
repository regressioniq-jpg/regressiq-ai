from typing import List, Dict
import chromadb
from sentence_transformers import SentenceTransformer
from data_loader import load_tests

MODEL_NAME = "all-MiniLM-L6-v2"
COLLECTION_NAME = "regressiq_tests"

_embedding_model = SentenceTransformer(MODEL_NAME)
_client = chromadb.Client()
_collection = _client.get_or_create_collection(COLLECTION_NAME)


def _test_to_document(test: Dict) -> str:
    return (
        f"Module: {test['module']}\n"
        f"Title: {test['title']}\n"
        f"Steps: {test['steps']}\n"
        f"Expected Result: {test['expected_result']}"
    )


def ingest_tests() -> int:
    tests = load_tests()

    existing = _collection.get()
    existing_ids = set(existing.get("ids", [])) if existing else set()

    new_docs = []
    new_ids = []
    new_embeddings = []
    new_metadatas = []

    for test in tests:
        test_id = test["test_id"]
        if test_id in existing_ids:
            continue

        doc = _test_to_document(test)
        embedding = _embedding_model.encode(doc).tolist()

        new_docs.append(doc)
        new_ids.append(test_id)
        new_embeddings.append(embedding)
        new_metadatas.append(
            {
                "module": test["module"],
                "title": test["title"]
            }
        )

    if new_ids:
        _collection.add(
            ids=new_ids,
            documents=new_docs,
            embeddings=new_embeddings,
            metadatas=new_metadatas
        )

    return len(new_ids)


def search_tests(query: str, n_results: int = 3) -> List[Dict]:
    query_embedding = _embedding_model.encode(query).tolist()

    results = _collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    ids = results.get("ids", [[]])[0]

    output = []
    for test_id, metadata, document in zip(ids, metadatas, documents):
        output.append(
            {
                "test_id": test_id,
                "module": metadata.get("module", ""),
                "title": metadata.get("title", ""),
                "document": document
            }
        )

    return output