import glob
import os

import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer

SPLITTER = "recursive"  # "recursive" (LangChain) or "simple" (our own split_text)

CHUNK_SIZE = 500
CHUNK_OVERLAP = 100

DOCS_DIR = "rag_docs"
CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "bid_docs"
MODEL_NAME = "all-MiniLM-L6-v2"
TOP_K = 3
PREVIEW_CHARS = 80

TEST_QUESTIONS = [
    "Is data encrypted?",
    "Can I claim a hotel on a business trip?",
    "What do we do when a critical incident happens?",
]


def split_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    """Split text into chunks of up to chunk_size characters, each overlapping the previous by overlap."""
    if not text:
        return []
    step = chunk_size - overlap
    chunks = []
    for start in range(0, len(text), step):
        chunks.append(text[start:start + chunk_size])
        if start + chunk_size >= len(text):
            break
    return chunks


recursive_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    separators=["\n\n", "\n", ". ", " ", ""],
)


def chunk_page(text):
    """Split one page of text using whichever splitter SPLITTER selects."""
    if SPLITTER == "recursive":
        return recursive_splitter.split_text(text)
    return split_text(text)


# --- Read and chunk every PDF, sorted by file name ---
pdf_paths = sorted(glob.glob(os.path.join(DOCS_DIR, "*.pdf")), key=os.path.basename)

ids = []
documents = []
metadatas = []
total_chunks = 0

for pdf_path in pdf_paths:
    file_name = os.path.basename(pdf_path)
    reader = PdfReader(pdf_path)
    file_chunks = 0
    for page_number, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text() or ""
        for chunk_number, chunk_text in enumerate(chunk_page(page_text), start=1):
            # Stable id: same file + page + chunk number always gives the same id.
            ids.append(f"{file_name}_p{page_number}_c{chunk_number}")
            documents.append(chunk_text)
            metadatas.append({"file_name": file_name, "page_number": page_number})
            file_chunks += 1
    print(f"{file_name}: {file_chunks} chunks")
    total_chunks += file_chunks

print(f"\nTotal: {total_chunks} chunks from {len(pdf_paths)} files")

# --- Embed ---
model = SentenceTransformer(MODEL_NAME)
embeddings = model.encode(documents).tolist()

# --- Start clean: delete the collection if it exists, then recreate it ---
client = chromadb.PersistentClient(path=CHROMA_PATH)
existing_names = [c.name if hasattr(c, "name") else c for c in client.list_collections()]
if COLLECTION_NAME in existing_names:
    client.delete_collection(COLLECTION_NAME)
collection = client.create_collection(name=COLLECTION_NAME)

collection.upsert(
    ids=ids,
    documents=documents,
    embeddings=embeddings,
    metadatas=metadatas,
)
print(f"Collection '{COLLECTION_NAME}' now holds {collection.count()} chunks")

# --- Test questions ---
for question in TEST_QUESTIONS:
    query_embedding = model.encode([question]).tolist()
    results = collection.query(query_embeddings=query_embedding, n_results=TOP_K)

    print(f'\nTop {TOP_K} results for: "{question}"')
    for metadata, distance, text in zip(
        results["metadatas"][0], results["distances"][0], results["documents"][0]
    ):
        preview = text[:PREVIEW_CHARS].replace("\n", " ")
        print(
            f"  {metadata['file_name']} | page {metadata['page_number']} | "
            f"distance {distance:.4f} | {preview}"
        )
