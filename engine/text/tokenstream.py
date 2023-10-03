from abc import ABC, abstractclassmethod, abstractmethod
from typing import Generator

class TokenStream(ABC):
    """Creates a sequence of string tokens from the contents of another stream, 
    breaking the bytes of the stream into tokens in some way."""

    @abstractmethod
    def __iter__(self):
        """Gets a sequence of tokens from the document that can be iterated over."""
        pass

    @abstractmethod
    def __enter__(self):
        pass

    @abstractmethod
    def __exit__(self):
        pass