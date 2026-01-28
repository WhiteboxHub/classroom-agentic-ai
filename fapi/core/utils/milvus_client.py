import os
from dotenv import load_dotenv
from collections import defaultdict
from typing import List, Dict, Any

from pymilvus import (
    connections,
    FieldSchema,
    CollectionSchema,
    DataType,
    Collection,
    utility,
)
from sentence_transformers import SentenceTransformer

# Load environment variables once
load_dotenv()


class MilvusChunkStore:
    """
    Static utility class for:
    - Connecting to Milvus
    - Creating collections
    - Enforcing indexing
    - Chunking text
    - Embedding text
    - Storing chunks with filename metadata
    """

    # -------------------------
    # Config from .env
    # -------------------------
    MILVUS_HOST = os.getenv("MILVUS_HOST", "localhost")
    MILVUS_PORT = os.getenv("MILVUS_PORT", "19530")
    MILVUS_ALIAS = os.getenv("MILVUS_ALIAS", "default")

    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", "384"))

    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))

    INDEX_METRIC = os.getenv("INDEX_METRIC", "IP")
    INDEX_TYPE = os.getenv("INDEX_TYPE", "HNSW")
    HNSW_M = int(os.getenv("HNSW_M", "16"))
    HNSW_EF_CONSTRUCTION = int(os.getenv("HNSW_EF_CONSTRUCTION", "200"))
    HNSW_EF_SEARCH = int(os.getenv("HNSW_EF_SEARCH", "128"))

    TOP_K = int(os.getenv("TOP_K", "20"))
    SEMANTIC_K = int(os.getenv("SEMANTIC_K", "50"))
    KEYWORD_K = int(os.getenv("KEYWORD_K", "50"))
    SEMANTIC_WEIGHT = float(os.getenv("SEMANTIC_WEIGHT", "0.7"))
    KEYWORD_WEIGHT = float(os.getenv("KEYWORD_WEIGHT", "0.3"))

    _model = SentenceTransformer(EMBEDDING_MODEL)

    # -------------------------
    # Connection
    # -------------------------
    @staticmethod
    def connect(
        host: str = None,
        port: str = None,
        alias: str = None,
    ) -> None:
        connections.connect(
            alias=alias or MilvusChunkStore.MILVUS_ALIAS,
            host=host or MilvusChunkStore.MILVUS_HOST,
            port=port or MilvusChunkStore.MILVUS_PORT,
        )

    # -------------------------
    # Collection
    # -------------------------
    @staticmethod
    def create_collection(
        collection_name: str,
        dim: int = None,
    ) -> Collection:
        if utility.has_collection(collection_name):
            return Collection(collection_name)

        fields = [
            FieldSchema(
                name="id",
                dtype=DataType.INT64,
                is_primary=True,
                auto_id=True,
            ),
            FieldSchema(
                name="embedding",
                dtype=DataType.FLOAT_VECTOR,
                dim=dim or MilvusChunkStore.EMBEDDING_DIM,
            ),
            FieldSchema(
                name="text",
                dtype=DataType.VARCHAR,
                max_length=8192,
            ),
            FieldSchema(
                name="filename",
                dtype=DataType.VARCHAR,
                max_length=512,
            ),
        ]

        schema = CollectionSchema(
            fields=fields,
            description="Document chunks with embeddings and filename metadata",
        )

        return Collection(
            name=collection_name,
            schema=schema,
        )

    # -------------------------
    # Index enforcement
    # -------------------------
    @staticmethod
    def enforce_index(collection: Collection) -> None:
        index_params = {
            "metric_type": MilvusChunkStore.INDEX_METRIC,
            "index_type": MilvusChunkStore.INDEX_TYPE,
            "params": {
                "M": MilvusChunkStore.HNSW_M,
                "efConstruction": MilvusChunkStore.HNSW_EF_CONSTRUCTION,
            },
        }

        if not collection.has_index():
            collection.create_index(
                field_name="embedding",
                index_params=index_params,
            )

        collection.load()

    # -------------------------
    # Chunking
    # -------------------------
    @staticmethod
    def chunk_text(
        text: str,
        chunk_size: int = None,
        overlap: int = None,
    ) -> List[str]:
        chunk_size = chunk_size or MilvusChunkStore.CHUNK_SIZE
        overlap = overlap or MilvusChunkStore.CHUNK_OVERLAP

        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size
            chunks.append(text[start:end])
            start = end - overlap

        return chunks

    # -------------------------
    # Embedding
    # -------------------------
    @staticmethod
    def embed_texts(texts: List[str]) -> List[List[float]]:
        embeddings = MilvusChunkStore._model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )
        return embeddings.tolist()

    # -------------------------
    # Storage
    # -------------------------
    @staticmethod
    def store_document(
        collection: Collection,
        text: str,
        filename: str,
    ) -> None:
        chunks = MilvusChunkStore.chunk_text(text)
        embeddings = MilvusChunkStore.embed_texts(chunks)

        data = [
            embeddings,
            chunks,
            [filename] * len(chunks),
        ]

        collection.insert(data)

    # -------------------------
    # Hybrid Retrieval
    # -------------------------
    @staticmethod
    def hybrid_retrieve(
        collection: Collection,
        query_embedding: List[float],
        query_text: str,
        top_k: int = None,
        semantic_k: int = None,
        keyword_k: int = None,
        semantic_weight: float = None,
        keyword_weight: float = None,
    ) -> List[Dict[str, Any]]:

        top_k = top_k or MilvusChunkStore.TOP_K
        semantic_k = semantic_k or MilvusChunkStore.SEMANTIC_K
        keyword_k = keyword_k or MilvusChunkStore.KEYWORD_K
        semantic_weight = semantic_weight or MilvusChunkStore.SEMANTIC_WEIGHT
        keyword_weight = keyword_weight or MilvusChunkStore.KEYWORD_WEIGHT

        # 1. Semantic search
        semantic_results = collection.search(
            data=[query_embedding],
            anns_field="embedding",
            param={
                "metric_type": MilvusChunkStore.INDEX_METRIC,
                "params": {"ef": MilvusChunkStore.HNSW_EF_SEARCH},
            },
            limit=semantic_k,
            output_fields=["text", "filename"],
        )

        semantic_scores = {}
        for hit in semantic_results[0]:
            semantic_scores[hit.id] = {
                "score": hit.score,
                "text": hit.entity.get("text"),
                "filename": hit.entity.get("filename"),
            }

        if semantic_scores:
            max_sem = max(v["score"] for v in semantic_scores.values())
            for v in semantic_scores.values():
                v["score"] /= max_sem

        # 2. Keyword search
        keyword_expr = f'text like "%{query_text}%"'
        keyword_results = collection.query(
            expr=keyword_expr,
            limit=keyword_k,
            output_fields=["id", "text", "filename"],
        )

        keyword_scores = {}
        for idx, row in enumerate(keyword_results):
            keyword_scores[row["id"]] = {
                "score": 1.0 / (idx + 1),
                "text": row["text"],
                "filename": row["filename"],
            }

        if keyword_scores:
            max_kw = max(v["score"] for v in keyword_scores.values())
            for v in keyword_scores.values():
                v["score"] /= max_kw

        # 3. Fusion
        fused = defaultdict(lambda: {
            "semantic_score": 0.0,
            "keyword_score": 0.0,
            "text": None,
            "filename": None,
        })

        for doc_id, v in semantic_scores.items():
            fused[doc_id]["semantic_score"] = v["score"]
            fused[doc_id]["text"] = v["text"]
            fused[doc_id]["filename"] = v["filename"]

        for doc_id, v in keyword_scores.items():
            fused[doc_id]["keyword_score"] = v["score"]
            fused[doc_id]["text"] = v["text"]
            fused[doc_id]["filename"] = v["filename"]

        results = []
        for doc_id, v in fused.items():
            final_score = (
                semantic_weight * v["semantic_score"]
                + keyword_weight * v["keyword_score"]
            )
            results.append({
                "id": doc_id,
                "score": final_score,
                "text": v["text"],
                "filename": v["filename"],
            })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]
