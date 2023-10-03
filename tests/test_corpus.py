from engine.documents import DocumentCorpus, DirectoryCorpus, JsonDocument, TextFileDocument
from pathlib import Path
import pytest
import tempfile
import os
import json

json_content = {"title": "test", "body": "This is a test json document."}

# Test for JsonDocument
def test_jsondocument():
    doc = JsonDocument(0, json_content["title"], json_content["body"])
    assert doc.title == "test"
    assert next(doc.get_content()) == "This is a test json document."

text_content = "This is a test text document."

# Test for TextFileDocument
def test_textfiledocument():
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp:
        tmp.write(text_content.encode())
        tmp.close()
        doc = TextFileDocument(1, Path(tmp.name))
        assert doc.title == Path(tmp.name).stem
        assert next(iter(doc.get_content())).strip() == text_content
        os.unlink(tmp.name)

# Test for DirectoryCorpus
def test_directorycorpus():
    with tempfile.TemporaryDirectory() as tmpdirname:
        json_path = os.path.join(tmpdirname, "doc1.json")
        text_path = os.path.join(tmpdirname, "doc2.txt")

        with open(json_path, "w") as f:
            json.dump(json_content, f)
        
        with open(text_path, "w") as f:
            f.write(text_content)

        corpus = DirectoryCorpus(Path(tmpdirname))
        assert len(corpus) == 2

        # Validate Document retrieval
        doc = corpus.get_document(0)
        assert doc is not None

        doc = corpus.get_document(999)
        assert doc is None