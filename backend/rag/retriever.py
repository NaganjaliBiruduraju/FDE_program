import re

from backend.embeddings.embedder import TextEmbedder
from backend.prompts.query_understanding import understand_query
from backend.vector_store.chroma_store import ChromaVectorStore


class RAGRetriever:
    """Retrieve relevant document chunks using hybrid retrieval."""

    def __init__(
        self,
        persist_directory: str = "documents/vector_db",
        collection_name: str = "document_chunks",
    ):
        self.embedder = TextEmbedder()

        self.vector_store = ChromaVectorStore(
            persist_directory=persist_directory,
            collection_name=collection_name,
        )

    def retrieve(
        self,
        query: str,
        file_name: str,
        top_k: int = 5,
    ) -> list[dict]:
        """Retrieve relevant chunks using semantic and lexical evidence."""

        if not isinstance(query, str):
            raise TypeError("query must be a string")

        if not query.strip():
            raise ValueError("query cannot be empty")

        if not isinstance(file_name, str):
            raise TypeError("file_name must be a string")

        if not file_name.strip():
            raise ValueError("file_name cannot be empty")

        if top_k <= 0:
            raise ValueError("top_k must be greater than 0")

        # 1. Understand the user query
        query_info = understand_query(query)

        # 2. Build a focused semantic search query
        search_query = self._build_search_query(
            query_info
        )

        # 3. Semantic retrieval
        semantic_results = self._semantic_retrieve(
            query=search_query,
            file_name=file_name,
            top_k=top_k * 2,
        )

        # 4. Keyword and concept retrieval
        keyword_results = self._keyword_retrieve(
            query_info=query_info,
            file_name=file_name,
        )

        # 5. Combine retrieval signals
        return self._combine_results(
            semantic_results=semantic_results,
            keyword_results=keyword_results,
            top_k=top_k,
        )

    def _build_search_query(
        self,
        query_info: dict,
    ) -> str:
        """Build a focused query for semantic retrieval."""

        parts = []

        primary_topic = query_info.get(
            "primary_topic"
        )

        if primary_topic:
            parts.append(primary_topic)

        concepts = query_info.get(
            "concepts",
            [],
        )

        for concept in concepts:
            if concept not in parts:
                parts.append(concept)

        keywords = query_info.get(
            "keywords",
            [],
        )

        for keyword in keywords:
            if keyword not in parts:
                parts.append(keyword)

        section_hint = query_info.get(
            "section_hint"
        )

        if section_hint and section_hint not in parts:
            parts.append(section_hint)

        if not parts:
            return query_info.get(
                "original_prompt",
                "",
            )

        return " ".join(parts)

    def _semantic_retrieve(
        self,
        query: str,
        file_name: str,
        top_k: int,
    ) -> list[dict]:
        """Retrieve chunks using embedding similarity."""

        query_embedding = self.embedder.embed_text(
            query
        )

        results = self.vector_store.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where={
                "file_name": file_name,
            },
        )

        retrieved_chunks = []

        for i in range(
            len(results["ids"][0])
        ):
            retrieved_chunks.append(
                {
                    "chunk_id": results["ids"][0][i],
                    "text": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i],
                }
            )

        return retrieved_chunks

    def _keyword_retrieve(
        self,
        query_info: dict,
        file_name: str,
    ) -> list[dict]:
        """Retrieve chunks using topics, concepts, and keywords."""

        results = self.vector_store.collection.get(
            where={
                "file_name": file_name,
            },
            include=[
                "documents",
                "metadatas",
            ],
        )

        primary_topic = query_info.get(
            "primary_topic"
        )

        concepts = query_info.get(
            "concepts",
            [],
        )

        keywords = query_info.get(
            "keywords",
            [],
        )

        section_hint = query_info.get(
            "section_hint"
        )

        keyword_results = []

        for i, text in enumerate(
            results["documents"]
        ):
            text_lower = text.lower()

            # Primary topic match
            primary_score = self._phrase_match_score(
                text=text_lower,
                phrase=primary_topic,
            )

            # Concept match
            concept_score = self._concept_match_score(
                text=text_lower,
                concepts=concepts,
            )

            # Individual keyword match
            term_score = self._keyword_match_score(
                text=text_lower,
                keywords=keywords,
            )

            # Section match
            section_score = self._phrase_match_score(
                text=text_lower,
                phrase=section_hint,
            )

            # Final lexical score
            keyword_score = (
                0.50 * primary_score
                + 0.25 * concept_score
                + 0.20 * term_score
                + 0.05 * section_score
            )

            if keyword_score == 0:
                continue

            keyword_results.append(
                {
                    "chunk_id": results["ids"][i],
                    "text": text,
                    "metadata": results["metadatas"][i],
                    "keyword_score": keyword_score,
                    "primary_score": primary_score,
                    "concept_score": concept_score,
                    "term_score": term_score,
                }
            )

        keyword_results.sort(
            key=lambda result: (
                result["keyword_score"],
                result["primary_score"],
                result["concept_score"],
                result["term_score"],
            ),
            reverse=True,
        )

        return keyword_results

    @staticmethod
    def _phrase_match_score(
        text: str,
        phrase: str | None,
    ) -> float:
        """Return 1 when a complete phrase appears in the text."""

        if not phrase:
            return 0.0

        phrase = phrase.lower().strip()

        if not phrase:
            return 0.0

        # Multi-word phrase
        if " " in phrase:
            return (
                1.0
                if phrase in text
                else 0.0
            )

        # Single-word phrase
        return (
            1.0
            if re.search(
                rf"\b{re.escape(phrase)}\b",
                text,
            )
            else 0.0
        )

    @staticmethod
    def _concept_match_score(
        text: str,
        concepts: list[str],
    ) -> float:
        """Calculate concept coverage."""

        if not concepts:
            return 0.0

        matches = sum(
            1
            for concept in concepts
            if RAGRetriever._phrase_match_score(
                text,
                concept,
            )
            > 0
        )

        return matches / len(concepts)

    @staticmethod
    def _keyword_match_score(
        text: str,
        keywords: list[str],
    ) -> float:
        """Calculate individual keyword coverage."""

        if not keywords:
            return 0.0

        matches = 0

        for keyword in keywords:
            keyword = keyword.lower().strip()

            if not keyword:
                continue

            if " " in keyword:
                if keyword in text:
                    matches += 1

            elif re.search(
                rf"\b{re.escape(keyword)}\b",
                text,
            ):
                matches += 1

        return matches / len(keywords)

    def _combine_results(
        self,
        semantic_results: list[dict],
        keyword_results: list[dict],
        top_k: int,
    ) -> list[dict]:
        """Combine semantic similarity with lexical evidence."""

        combined = {}

        # Add semantic results
        for rank, result in enumerate(
            semantic_results,
            start=1,
        ):
            chunk_id = result["chunk_id"]

            combined[chunk_id] = {
                **result,
                "semantic_rank": rank,
                "keyword_rank": None,
                "keyword_score": 0.0,
                "primary_score": 0.0,
                "concept_score": 0.0,
                "term_score": 0.0,
                "fusion_score": 0.0,
            }

        # Add keyword results
        for rank, result in enumerate(
            keyword_results,
            start=1,
        ):
            chunk_id = result["chunk_id"]

            if chunk_id not in combined:
                combined[chunk_id] = {
                    **result,
                    "distance": None,
                    "semantic_rank": None,
                    "keyword_rank": rank,
                    "keyword_score": result[
                        "keyword_score"
                    ],
                    "primary_score": result.get(
                        "primary_score",
                        0.0,
                    ),
                    "concept_score": result.get(
                        "concept_score",
                        0.0,
                    ),
                    "term_score": result.get(
                        "term_score",
                        0.0,
                    ),
                    "fusion_score": 0.0,
                }

            else:
                combined[chunk_id][
                    "keyword_rank"
                ] = rank

                combined[chunk_id][
                    "keyword_score"
                ] = result["keyword_score"]

                combined[chunk_id][
                    "primary_score"
                ] = result.get(
                    "primary_score",
                    0.0,
                )

                combined[chunk_id][
                    "concept_score"
                ] = result.get(
                    "concept_score",
                    0.0,
                )

                combined[chunk_id][
                    "term_score"
                ] = result.get(
                    "term_score",
                    0.0,
                )

        # Get semantic distance range
        distances = [
            result["distance"]
            for result in combined.values()
            if result.get("distance") is not None
        ]

        min_distance = (
            min(distances)
            if distances
            else 0.0
        )

        max_distance = (
            max(distances)
            if distances
            else 1.0
        )

        # Calculate final score
        for result in combined.values():
            distance = result.get(
                "distance"
            )

            if distance is None:
                semantic_score = 0.0

            elif max_distance == min_distance:
                semantic_score = 1.0

            else:
                semantic_score = (
                    max_distance - distance
                ) / (
                    max_distance - min_distance
                )

            keyword_score = result.get(
                "keyword_score",
                0.0,
            )

            primary_score = result.get(
                "primary_score",
                0.0,
            )

            concept_score = result.get(
                "concept_score",
                0.0,
            )

            result["semantic_score"] = (
                semantic_score
            )

            # Final hybrid score
            result["fusion_score"] = (
                0.45 * semantic_score
                + 0.35 * primary_score
                + 0.15 * keyword_score
                + 0.05 * concept_score
            )

        ranked_results = sorted(
            combined.values(),
            key=lambda result: (
                result["fusion_score"],
                result.get(
                    "semantic_score",
                    0.0,
                ),
                result.get(
                    "primary_score",
                    0.0,
                ),
            ),
            reverse=True,
        )

        return ranked_results[:top_k]

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        """Convert text into searchable terms."""

        return re.findall(
            r"\b[a-zA-Z0-9]+\b",
            text.lower(),
        )