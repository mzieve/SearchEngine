from .tokenprocessor import TokenProcessor
from stemming.porter2 import stem  # type: ignore
import re


class BasicTokenProcessor(TokenProcessor):
    def __init__(self):
        super().__init__()

    def process_token(self, token: str) -> list:
        result_types = []

        # Handle hyphens
        if "-" in token:
            split_tokens = token.split("-")
            combined_tokens = "".join(split_tokens)
            result_types.extend(split_tokens)
            result_types.append(combined_tokens)
        else:
            result_types.append(token)

        # Cleaning and processing the result types
        cleaned_types = []
        for tok in result_types:
            # Remove non-alphanumeric characters from the beginning and end
            tok = re.sub(r"^[^a-zA-Z0-9]+|[^a-zA-Z0-9]+$", "", tok)
            # Remove apostrophes or quotation marks
            tok = re.sub(r"[\"']", "", tok)
            # Convert to lowercase
            tok = tok.lower()
            cleaned_types.append(tok)

        return cleaned_types

    def normalize_type(self, type_: str) -> str:
        # Stem using the Porter2 Stemmer
        return stem(type_)
