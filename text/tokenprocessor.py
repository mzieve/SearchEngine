from abc import ABC, abstractmethod

class TokenProcessor(ABC):
	"""A TokenProcessor that processes tokesn into types and normalizes types into terms"""

	@abstractmethod
	def process_token(self, token):
		"""Processes tokens into types"""
		pass

	@abstractmethod
	def normalize_type(self, type_):
		"""Normalizes types into terms"""
		pass