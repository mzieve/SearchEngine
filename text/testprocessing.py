import pytest
import io
from text.basictokenprocessor import BasicTokenProcessor
from text.englishtokenstream import EnglishTokenStream

processor = BasicTokenProcessor()

# English Stream Function
def process_stream(source_text):
    source = io.StringIO(source_text)
    stream = EnglishTokenStream(source)
    processed_tokens = [processor.process_token(token) for token in stream]
    return [item for sublist in processed_tokens for item in sublist]

# Unit test for processing and normalizing according to assignment requirements 
def test_punctuation_removal():
    assert process_stream("Hello, world!") == ["hello", "world"]

def test_tokenization():
    assert process_stream("This is a sentence") == ["this", "is", "a", "sentence"]

def test_lowercase():
    assert process_stream("Hello World") == ["hello", "world"]

def test_beg_end():
    assert process_stream("Hello.") == ["hello"]
    assert process_stream("192.168.1.1") == ["192.168.1.1"]

def test_hyphens():
    assert process_stream("Hewlett-Packard-Computing") == ["hewlett", "packard", "computing", "hewlettpackardcomputing"]

def test_stemming():
    assert processor.normalize_type("running") == "run"
    assert processor.normalize_type("runner") == "runner"

