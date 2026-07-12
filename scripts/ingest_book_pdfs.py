"""Process all PDFs in knowledge-base/books/Book PDFs into the Chroma vector store."""
import os
import sys
from pathlib import Path

sys.path.insert(0, "backend/src")
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from divyadrishti.documents import (
    ChromaVectorStore,
    DocumentProcessingPipeline,
    SentenceTransformerEmbeddingProvider,
)

PDF_DIR = Path("knowledge-base/books/Book PDFs")
PERSIST_DIR = Path(".chroma")

# Reduce model download warnings
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"


def clean_book_id(filename: str) -> str:
    """Convert a filename into a safe book_id."""
    base = Path(filename).stem
    return "".join(c if c.isalnum() or c in "_-" else "_" for c in base)


def main() -> None:
    pipeline = DocumentProcessingPipeline(
        embedder=SentenceTransformerEmbeddingProvider(
            "paraphrase-multilingual-MiniLM-L12-v2"
        ),
        vector_store=ChromaVectorStore(persist_dir=PERSIST_DIR),
    )

    pdf_files = sorted(PDF_DIR.glob("*.pdf"))
    print(f"Found {len(pdf_files)} PDFs to process")

    for pdf_path in pdf_files:
        book_id = clean_book_id(pdf_path.name)
        result = pipeline.process(
            pdf_path,
            book_id=book_id,
            book_title=pdf_path.stem,
        )
        print(
            f"{pdf_path.name}: chunks={result.chunk_count}, "
            f"stored={result.stored}, language={result.language}, "
            f"errors={result.errors[:1]}"
        )


if __name__ == "__main__":
    main()
