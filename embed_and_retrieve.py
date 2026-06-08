"""
embed_and_retrieve.py
---------------------
Milestone 4 — Embedding and Retrieval Pipeline
McNeese State University Professor Reviews RAG System
"""

import re
import chromadb
from sentence_transformers import SentenceTransformer
from ingest_and_chunk import ingest_all

# ── Configuration ─────────────────────────────────────────────────────────────

COLLECTION_NAME = "professor_reviews"
EMBEDDING_MODEL  = "all-MiniLM-L6-v2"
TOP_K            = 5

KNOWN_PROFESSORS = [
    "Andrew Mudd",
    "Bei Xie",
    "Constance Kersten",
    "Jennifer Lavergne",
    "Lara Guidroz",
    "Lyle Hardee",
    "Shaikh Samad",
    "Susie Beasley",
    "Tristan Salinas",
    "Vipin Menon",
]

# ── Step 1: Set up embedding model ────────────────────────────────────────────

print("[INFO] Loading embedding model...")
model = SentenceTransformer(EMBEDDING_MODEL)
print(f"[INFO] Model loaded: {EMBEDDING_MODEL}\n")

# ── Step 2: Set up ChromaDB — always start fresh, use cosine distance ─────────

client = chromadb.Client()

try:
    client.delete_collection(name=COLLECTION_NAME)
    print(f"[INFO] Deleted existing collection, starting fresh.")
except Exception:
    pass

collection = client.get_or_create_collection(
    name=COLLECTION_NAME,
    metadata={"hnsw:space": "cosine"}
)

# ── Step 3: Embed and load chunks into ChromaDB ───────────────────────────────

def embed_and_store(chunks: list[dict]):
    print(f"[INFO] Embedding {len(chunks)} chunks and storing in ChromaDB...")

    documents  = []
    embeddings = []
    metadatas  = []
    ids        = []

    for i, chunk in enumerate(chunks):
        text      = chunk["text"]
        embedding = model.encode(text).tolist()

        metadata = {
            "professor":  chunk["professor"],
            "department": chunk["department"],
            "course":     chunk["course"],
            "date":       chunk["date"],
            "rating":     chunk["rating"] if chunk["rating"] is not None else -1.0,
        }

        documents.append(text)
        embeddings.append(embedding)
        metadatas.append(metadata)
        ids.append(f"chunk_{i}")

    collection.add(
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids,
    )

    print(f"[INFO] Successfully stored {len(chunks)} chunks in ChromaDB.\n")


# ── Step 4: Query type detection ──────────────────────────────────────────────

def detect_query_type(query: str) -> dict:
    query_lower = query.lower()

    matched_professor = None
    for prof in KNOWN_PROFESSORS:
        last_name = prof.split()[-1].lower()
        if last_name in query_lower or prof.lower() in query_lower:
            matched_professor = prof
            break

    course_match   = re.search(r'\b[A-Z]{2,5}\s*\d{3,4}[A-Z]?\b', query, re.IGNORECASE)
    matched_course = course_match.group(0).upper().replace(" ", "") if course_match else None

    if matched_professor:
        return {"type": "single_professor", "professor": matched_professor, "course": matched_course}
    elif matched_course:
        return {"type": "comparative", "professor": None, "course": matched_course}
    else:
        return {"type": "general", "professor": None, "course": None}


# ── Step 5: Out-of-scope check ────────────────────────────────────────────────

def is_out_of_scope(query: str) -> str | None:
    name_patterns = re.findall(
        r'\b(?:professor|prof|dr\.?|mr\.?|mrs\.?|ms\.?)\s+([A-Z][a-z]+)',
        query, re.IGNORECASE
    )

    known_last_names  = {prof.split()[-1].lower() for prof in KNOWN_PROFESSORS}
    known_first_names = {prof.split()[0].lower()  for prof in KNOWN_PROFESSORS}

    for name in name_patterns:
        name_lower = name.lower()
        if name_lower not in known_last_names and name_lower not in known_first_names:
            return (
                f"I don't have reviews for a professor named '{name}' in the current dataset. "
                f"Available professors: {', '.join(KNOWN_PROFESSORS)}."
            )
    return None


# ── Step 6: Retrieval function ────────────────────────────────────────────────

def retrieve(query: str, top_k: int = TOP_K) -> list[dict]:
    oos = is_out_of_scope(query)
    if oos:
        print(f"\n[OUT OF SCOPE] {oos}")
        return []

    query_info = detect_query_type(query)
    print(f"\n[QUERY TYPE] {query_info['type']}")
    if query_info["professor"]:
        print(f"[FILTER] Professor: {query_info['professor']}")
    if query_info["course"]:
        print(f"[FILTER] Course: {query_info['course']}")

    where_filter = None
    if query_info["type"] == "single_professor":
        where_filter = {"professor": {"$eq": query_info["professor"]}}
    elif query_info["type"] == "comparative" and query_info["course"]:
        where_filter = {"course": {"$eq": query_info["course"]}}

    query_embedding = model.encode(query).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where=where_filter,
        include=["documents", "metadatas", "distances"],
    )

    chunks_out = []
    for doc, meta, dist in zip(results["documents"][0], results["metadatas"][0], results["distances"][0]):
        chunks_out.append({
            "text":      doc,
            "professor": meta["professor"],
            "course":    meta["course"],
            "date":      meta["date"],
            "rating":    meta["rating"],
            "distance":  round(dist, 4),
        })

    return chunks_out


# ── Step 7: Print retrieval results ──────────────────────────────────────────

def print_results(query: str, results: list[dict]):
    print(f"\nQuery: {query}")
    print("="*70)
    if not results:
        print("No results returned.")
        return
    for i, r in enumerate(results, 1):
        print(f"\n  Result {i} (distance: {r['distance']})")
        print(f"  Professor : {r['professor']}")
        print(f"  Course    : {r['course']}")
        print(f"  Date      : {r['date']}")
        print(f"  Rating    : {r['rating']}")
        print(f"  Text      : {r['text']}")
    print("="*70)


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    chunks = ingest_all()
    embed_and_store(chunks)

    print(f"[INFO] ChromaDB collection has {collection.count()} chunks.\n")

    test_queries = [
        "Does Hardee give partial credit on exams?",
        "Who should I prefer taking CSCI309 with?",
        "Should I go through past quizzes and exams to prepare for Lavergne's final?",
    ]

    for query in test_queries:
        results = retrieve(query)
        print_results(query, results)
