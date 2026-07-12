"""Check which PDFs in Book PDFs have extractable text."""
import sys
from pathlib import Path

import fitz

pdf_dir = Path("knowledge-base/books/Book PDFs")
results = []

for p in sorted(pdf_dir.glob("*.pdf")):
    try:
        doc = fitz.open(p)
        chars = 0
        for i in range(min(3, len(doc))):
            text = doc[i].get_text()
            chars += len(text.strip())
        results.append((chars, p.name))
    except Exception as exc:
        results.append((-1, f"{p.name}: {exc}"))

results.sort(reverse=True)
print(f"Checked {len(results)} PDFs")
for chars, name in results[:20]:
    print(f"{chars:>8}  {name}")
