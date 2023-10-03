from .tokenprocessor import TokenProcessor
from nltk.stem import PorterStemmer
import re

class BasicTokenProcessor(TokenProcessor):
	"""A Basic Token Proccesor that handles hyphens, removes all non-alphanumeric characters, removes 
	all apostophes or quotation marks anywhere within the token, and converts tokens to lowercase. Then 
	uses Porter2 Stemmer to normalize types into terms."""
	def __init__(self):
		self.stemmer = PorterStemmer()

	def process_token(self, token: str):
		# Process Tokens Into Types
		# Remove non-alphanumeric characters
		token = re.sub(r'[^a-zA-Z0-9]', '', token)
		# Lowercase all tokens
		token = token.lower()

		# Hyphens
		if '-' in token:
			split_tokens = token.split('-')
			combined_tokens = ''.join(split_tokens)
			result_types = split_tokens + [combined_tokens]
		else:
			result_types = [token]

		return result_types

	def normalize_type(self, type: str):
		# Normalize Types into Terms
		return self.stemmer.stem(type)