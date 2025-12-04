# ivf_backend/services/rag_engine.py

import json
import logging
import copy
from typing import List, Dict, Any, Optional
from collections import OrderedDict
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from supabase import create_client
from pathlib import Path

from ..config import settings

logger = logging.getLogger(__name__)


# ---------------------------------------------------------
# IVF-ONLY QUESTION FILTER
# ---------------------------------------------------------
IVF_KEYWORDS = [
    "ivf", "fertility", "infertility", "egg", "oocyte", "sperm",
    "embryo", "endometrium", "uterus", "ovary", "fallopian",
    "hormone", "amh", "fsh", "lh", "blastocyst", "implantation",
    "embryologist", "icsi", "iui", "transfer", "follicle",
    "stimulation", "hcg", "progesterone", "endocrine",
    "zona pellucida", "andrology", "retrieval", "transfer",
    "beta hcg", "pcos", "endometriosis", "estrogen",
    "follicular", "ovulation"
]


def is_ivf_question(q: str) -> bool:
    q = q.lower()
    return any(k in q for k in IVF_KEYWORDS)


class RAGEngine:
    """
    IVF-specific RAG Engine with strict IVF-only filtering.
    """

    def __init__(self):
        self.embedding_model: Optional[SentenceTransformer] = None
        self.faiss_index = None
        self.id_map: Dict[str, str] = {}

        # Supabase
        self.supabase_client = None

        # Caches
        self._emb_cache: OrderedDict[str, np.ndarray] = OrderedDict()
        self._emb_cache_max = 256

        self._query_cache: OrderedDict[str, List[Dict[str, Any]]] = OrderedDict()
        self._query_cache_max = 512

        self._initialize_components()

    # ---------------------------------------------------------
    # Initialization
    # ---------------------------------------------------------
    def _initialize_components(self):
        try:
            # Load embedding model
            try:
                self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
                logger.info(f"Loaded embedding model: {settings.EMBEDDING_MODEL}")
            except Exception as e:
                logger.error(f"Failed to load embedding model: {e}")
                self.embedding_model = None

            # Supabase
            try:
                if settings.SUPABASE_URL and settings.SUPABASE_KEY:
                    self.supabase_client = create_client(
                        settings.SUPABASE_URL, settings.SUPABASE_KEY
                    )
                    logger.info("Supabase client initialized.")
                else:
                    logger.warning("Supabase credentials missing.")
            except Exception as e:
                logger.error(f"Supabase init failed: {e}")
                self.supabase_client = None

            # FAISS
            self._load_faiss_index()

        except Exception as e:
            logger.error(f"RAG init failure: {e}")
            raise

    # ---------------------------------------------------------
    def _load_faiss_index(self):
        """Load FAISS index + ID map."""
        try:
            data_dir = Path(__file__).resolve().parents[1] / "data"
            index_path = data_dir / "ivf_faiss_index.index"
            id_map_path = data_dir / "faiss_id_map.json"

            if not index_path.exists():
                logger.error(f"FAISS index missing at: {index_path}")
                return

            self.faiss_index = faiss.read_index(str(index_path))
            logger.info("FAISS index loaded")

            if id_map_path.exists():
                with open(id_map_path, "r", encoding="utf-8") as f:
                    self.id_map = json.load(f)
                logger.info(f"ID map loaded: {len(self.id_map)} entries")
            else:
                logger.warning("ID map missing")
                self.id_map = {}

            # Verify dimension match
            if self.embedding_model:
                emb_dim = self.embedding_model.get_sentence_embedding_dimension()
                index_dim = self.faiss_index.d
                if emb_dim != index_dim:
                    logger.error(
                        f"Dimension mismatch: FAISS={index_dim}, Model={emb_dim}. Disabling FAISS."
                    )
                    self.faiss_index = None
                    return

            logger.info(f"FAISS dimension validated: {self.faiss_index.d}")

        except Exception as e:
            logger.error(f"Error loading FAISS: {e}")
            self.faiss_index = None
            self.id_map = {}

    # ---------------------------------------------------------
    # Embedding
    # ---------------------------------------------------------
    def get_embedding(self, text: str) -> np.ndarray:
        if not self.embedding_model:
            raise ValueError("Embedding model not initialized.")

        # Cache hit
        if text in self._emb_cache:
            emb = self._emb_cache.pop(text)
            self._emb_cache[text] = emb
            return emb

        emb = self.embedding_model.encode([text], normalize_embeddings=True)
        arr = np.array(emb, dtype=np.float32)

        self._emb_cache[text] = arr
        if len(self._emb_cache) > self._emb_cache_max:
            self._emb_cache.popitem(last=False)

        return arr

    # ---------------------------------------------------------
    # Query cache
    # ---------------------------------------------------------
    def _cache_key(self, query: str, top_k: int) -> str:
        return f"{query.strip().lower()}||{top_k}"

    def _get_cached_results(self, key: str):
        if key in self._query_cache:
            v = self._query_cache.pop(key)
            self._query_cache[key] = v
            return copy.deepcopy(v)
        return None

    def _set_cached_results(self, key: str, results: List[Dict[str, Any]]):
        light = [{"id": r["id"], "similarity_score": r["similarity_score"]} for r in results]
        self._query_cache[key] = light

        if len(self._query_cache) > self._query_cache_max:
            self._query_cache.popitem(last=False)

    # ---------------------------------------------------------
    # MAIN SEARCH – IVF RESTRICTION APPLIED HERE 🔥
    # ---------------------------------------------------------
    def search_similar_chunks(self, query: str, top_k: int = None) -> List[Dict[str, Any]]:
        # -------------------------------------------
        # BLOCK NON-IVF QUESTIONS IMMEDIATELY
        # -------------------------------------------
        if not is_ivf_question(query):
            logger.info(f"Blocked non-IVF query: {query}")
            return []      # empty → LLM fallback handles IVF-only message

        if top_k is None:
            top_k = settings.SIMILARITY_TOP_K

        key = self._cache_key(query, top_k)

        # Cache
        cached = self._get_cached_results(key)
        if cached:
            results = []
            for c in cached:
                chunk = self._get_chunk_by_id(c["id"])
                if chunk:
                    chunk["similarity_score"] = c["similarity_score"]
                    results.append(chunk)
            return results

        # No FAISS
        if not self.faiss_index:
            return self._search_direct_from_db(query, top_k)

        try:
            query_emb = self.get_embedding(query)
            distances, indices = self.faiss_index.search(query_emb, top_k)

            results = []
            for dist, idx in zip(distances[0], indices[0]):
                if idx == -1:
                    continue

                idx_str = str(idx)
                if idx_str not in self.id_map:
                    continue

                similarity = float(1.0 / (1.0 + dist))
                if similarity < settings.SIMILARITY_THRESHOLD:
                    continue

                chunk_id = self.id_map[idx_str]
                chunk = self._get_chunk_by_id(chunk_id)
                if chunk:
                    chunk["id"] = chunk_id
                    chunk["similarity_score"] = similarity
                    results.append(chunk)

            self._set_cached_results(key, results)
            return results

        except Exception as e:
            logger.error(f"FAISS search failed: {e}")
            return self._search_direct_from_db(query, top_k)

    # ---------------------------------------------------------
    # Supabase fallback
    # ---------------------------------------------------------
    def _search_direct_from_db(self, query: str, top_k: int):
        if not self.supabase_client:
            return []

        try:
            res = (
                self.supabase_client
                .table("ivf_chunks")
                .select("*")
                .ilike("chunk_text", f"%{query}%")
                .limit(top_k)
                .execute()
            )

            data = getattr(res, "data", []) or []
            for d in data:
                d["similarity_score"] = 0.55

            return data

        except Exception as e:
            logger.error(f"DB fallback failed: {e}")
            return []

    # ---------------------------------------------------------
    def _get_chunk_by_id(self, chunk_id: str):
        if not self.supabase_client:
            return None

        try:
            res = (
                self.supabase_client
                .table("ivf_chunks")
                .select("*")
                .eq("id", chunk_id)
                .limit(1)
                .execute()
            )

            data = getattr(res, "data", None)
            return data[0] if data else None

        except Exception as e:
            logger.error(f"Error retrieving chunk {chunk_id}: {e}")
            return None

    # ---------------------------------------------------------
    def format_context(self, chunks: List[Dict[str, Any]]) -> str:
        if not chunks:
            return "No relevant IVF information found."

        lines = ["Relevant IVF Information:"]
        for i, c in enumerate(chunks, start=1):
            lines.append(f"\n{i}. [Category: {c.get('category', 'General')}]")
            if c.get("question"):
                lines.append(f"   Q: {c.get('question')}")
            lines.append(f"   A: {c.get('answer', c.get('chunk_text', ''))}")

        return "\n".join(lines)
