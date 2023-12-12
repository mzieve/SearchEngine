import numpy as np
import nltk
nltk.download('words')
from nltk.corpus import words
import re

class SpellingCorrection:
    def __init__(self, index):
        """
        Initializes the SpellingCorrection class with a given index.
        
        :param index: An instance of PositionalInvertedIndex or similar that provides access to the vocabulary.
        """
        self.index = index
        self.dictionary = set(words.words())

    def get_kgrams(self, word, k):
        """ Returns the set of k-grams for the given word. """
        return set([word[i:i+k] for i in range(len(word) - k + 1)])

    def jaccard_coefficient(self, word, query_kgrams, k):
        word_kgrams = self.get_kgrams(word, k)
        intersection = len(query_kgrams.intersection(word_kgrams))
        union = len(query_kgrams) + len(word_kgrams) - intersection
        return intersection / union if union != 0 else 0

    def suggest_corrections_for_word(self, word, k, max_suggestions=5):
        query_kgrams = self.get_kgrams(word, k)
        scored_words = [(dict_word, self.jaccard_coefficient(dict_word, query_kgrams, k)) for dict_word in self.dictionary]
        ranked_candidates = sorted(scored_words, key=lambda x: x[1], reverse=True)
        return [candidate[0] for candidate in ranked_candidates[:max_suggestions]]

    def suggest_corrections(self, query, k=5, max_suggestions=5):
        corrected_words = []
        # Remove non-letter characters and split the query into individual words
        for word in re.sub(r'[^a-zA-Z\s]', '', query).split():
            suggestions = self.suggest_corrections_for_word(word, k, max_suggestions)
            corrected_word = suggestions[0] if suggestions else word
            corrected_words.append(corrected_word)
        return ' '.join(corrected_words)