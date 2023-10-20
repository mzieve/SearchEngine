from engine.querying import (
    AndQuery,
    BooleanQueryParser,
    OrQuery,
    NotQuery,
    TermLiteral,
    PhraseLiteral,
)
from engine.indexing import Posting
from engine.text import Preprocessing
import pytest
import config

config.LANGUAGE = "english"
preprocessor = Preprocessing()


def test_parse_simple_query():
    query_str = "cat dog"
    query_component = BooleanQueryParser.parse_query(query_str, preprocessor)
    assert isinstance(query_component, AndQuery)
    assert len(query_component.components) == 2
    assert isinstance(query_component.components[0], TermLiteral)
    assert query_component.components[0].term == "cat"
    assert isinstance(query_component.components[1], TermLiteral)
    assert query_component.components[1].term == "dog"


def test_parse_or_query():
    query_str = "cat + dog"
    query_component = BooleanQueryParser.parse_query(query_str, preprocessor)
    assert isinstance(query_component, OrQuery)
    assert len(query_component.components) == 2
    assert isinstance(query_component.components[0], TermLiteral)
    assert query_component.components[0].term == "cat"
    assert isinstance(query_component.components[1], TermLiteral)
    assert query_component.components[1].term == "dog"


def test_parse_mixed_query():
    query_str = 'cat dog + mouse "quick fox"'
    query_component = BooleanQueryParser.parse_query(query_str, preprocessor)
    assert isinstance(query_component, OrQuery)
    assert len(query_component.components) == 2
    assert isinstance(query_component.components[0], AndQuery)
    assert len(query_component.components[0].components) == 2
    assert isinstance(query_component.components[1], AndQuery)


def test_and_not_query():
    query_str = "cat -dog"
    query_component = BooleanQueryParser.parse_query(query_str, preprocessor)
    assert isinstance(query_component, AndQuery)
    assert len(query_component.components) == 2
    assert isinstance(query_component.components[0], TermLiteral)
    assert query_component.components[0].term == "cat"
    assert isinstance(query_component.components[1], NotQuery)
    assert query_component.components[1].component.term == "dog"
