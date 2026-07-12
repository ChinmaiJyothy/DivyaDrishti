import json
from pathlib import Path

import pytest

from divyadrishti.knowledge import KnowledgeRepository
from divyadrishti.learning import FeedbackManager, KnowledgeExporter


def test_export_knowledge_base_json(tmp_path):
    repo = KnowledgeRepository("knowledge-base")
    repo.load()
    exporter = KnowledgeExporter(repo)
    out = tmp_path / "kb.json"
    exporter.export_knowledge_base(out, "json")
    data = json.loads(out.read_text())
    assert isinstance(data, list)


def test_export_knowledge_base_csv(tmp_path):
    repo = KnowledgeRepository("knowledge-base")
    repo.load()
    exporter = KnowledgeExporter(repo)
    out = tmp_path / "kb.csv"
    exporter.export_knowledge_base(out, "csv")
    assert out.exists()
