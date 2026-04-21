import os
import chromadb
from chromadb.utils import embedding_functions

CHROMA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "chroma_store")
COLLECTION_NAME = "policy_documents"


def get_collection():
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=ef
    )
    return collection


def search_policies(query: str, n_results: int = 4) -> str:
    """Search policy documents for relevant information."""
    import json
    try:
        collection = get_collection()
        count = collection.count()
        if count == 0:
            return json.dumps({"message": "No policy documents have been uploaded yet."})

        results = collection.query(
            query_texts=[query],
            n_results=min(n_results, count)
        )

        output = []
        for i, doc in enumerate(results["documents"][0]):
            output.append({
                "chunk": doc,
                "source": results["metadatas"][0][i].get("source", "Unknown"),
                "page": results["metadatas"][0][i].get("page", "N/A"),
            })
        return json.dumps(output)
    except Exception as e:
        return json.dumps({"error": str(e)})


def list_uploaded_documents() -> str:
    """List all policy documents currently in the knowledge base."""
    import json
    try:
        collection = get_collection()
        count = collection.count()
        if count == 0:
            return json.dumps({"message": "No documents uploaded yet.", "total_chunks": 0})

        results = collection.get(include=["metadatas"])
        sources = list(set(
            m.get("source", "Unknown") for m in results["metadatas"]
        ))
        return json.dumps({
            "total_chunks": count,
            "documents": sources
        })
    except Exception as e:
        return json.dumps({"error": str(e)})


def ingest_pdf(file_path: str) -> str:
    """Ingest a PDF file into the vector store."""
    import json
    from pypdf import PdfReader

    try:
        reader = PdfReader(file_path)
        filename = os.path.basename(file_path)
        chunks = []
        metadatas = []
        ids = []

        for page_num, page in enumerate(reader.pages):
            text = page.extract_text()
            if not text or not text.strip():
                continue

            # Split page into chunks of ~500 chars with overlap
            chunk_size = 500
            overlap = 50
            start = 0
            chunk_idx = 0
            while start < len(text):
                end = start + chunk_size
                chunk = text[start:end].strip()
                if chunk:
                    chunks.append(chunk)
                    metadatas.append({
                        "source": filename,
                        "page": str(page_num + 1),
                        "chunk_index": str(chunk_idx)
                    })
                    ids.append(f"{filename}_p{page_num+1}_c{chunk_idx}")
                    chunk_idx += 1
                start = end - overlap

        if not chunks:
            return json.dumps({"error": "No text could be extracted from the PDF."})

        collection = get_collection()
        # Add in batches to avoid hitting limits
        batch_size = 50
        for i in range(0, len(chunks), batch_size):
            collection.upsert(
                documents=chunks[i:i+batch_size],
                metadatas=metadatas[i:i+batch_size],
                ids=ids[i:i+batch_size]
            )

        return json.dumps({
            "success": True,
            "filename": filename,
            "pages_processed": len(reader.pages),
            "chunks_stored": len(chunks)
        })
    except Exception as e:
        return json.dumps({"error": str(e)})