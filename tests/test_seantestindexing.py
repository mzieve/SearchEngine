import os.path
from pathlib import Path
from tkinter import filedialog
import sys

from engine.documents import DocumentCorpus, DirectoryCorpus, TextFileDocument, JsonDocument
from engine.indexing import Index, PositionalInvertedIndex
from engine.text import BasicTokenProcessor, EnglishTokenStream

"""This basic program builds a positional inverted index over the .txt files 
in the Path that is given."""


"""
def index_corpus(corpus: DocumentCorpus, token_processor: BasicTokenProcessor) -> Index:

    # Create a PositionalInvertedIndex object.
    p_i_index = PositionalInvertedIndex()
    for d in corpus:
        #   Tokenize the document's content by creating an EnglishTokenStream around the document's .content()
        content = d.get_content()
        token_stream = EnglishTokenStream(content)
        #   Iterate through the token stream, processing each with token_processor's process_token method.
        position = 0
        for token in token_stream:
            position += 1
            types = token_processor.process_token(token)
            # Normalize each type into a term, then add the term and its docID and position into the index.
            for type in types:
                term = token_processor.normalize_type(type)
                p_i_index.addTerm(term, d.id, position)
    return p_i_index

folder_selected = filedialog.askdirectory()

if folder_selected:
    corpus_path = Path(folder_selected)
    extension_factories = {
        '.txt': TextFileDocument.load_from,
        '.json': JsonDocument.load_from
    }
    d = DirectoryCorpus.load_directory(corpus_path, extension_factories)

    # Build the index over this directory.
    token_processor = BasicTokenProcessor()
    index = index_corpus(d, token_processor)
    print("Corpus loaded! Ready to search.")
    # We aren't ready to use a full query parser;
    # for now, we'll only support single-term queries.

    query = ""
    while (query != "quit"):
        query = input("Enter a word you want to search for in this corpus: ")
        query_types = token_processor.process_token(query)
        for query_type in query_types:
            query_term = token_processor.normalize_type(query_type)
            for p in index.getPostings(query_term):
                doc = d.get_document(p.doc_id)
                print("Doc ID {}. \"{}\" at positions {}".format(p.doc_id, doc.title, p.positions))
"""