import re

class SpellingCorrection:
    def __init__(self, index):
        self.index = index
        self.dictionary = set(self.index.getVocabulary())

    def levenshtein_distance(self, s1, s2):
        if len(s1) < len(s2):
            return self.levenshtein_distance(s2, s1)

        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]

    def suggest_corrections_for_word(self, word, max_suggestions=5):
        scored_words = [(dict_word, self.levenshtein_distance(dict_word, word)) for dict_word in self.dictionary]
        ranked_candidates = sorted(scored_words, key=lambda x: x[1], reverse=False)
        return [candidate[0] for candidate in ranked_candidates[:max_suggestions]]

    def suggest_corrections(self, query, max_suggestions=5):
        corrected_words = []
        for word in re.sub(r'[^a-zA-Z\s]', '', query).split():
            suggestions = self.suggest_corrections_for_word(word, max_suggestions)
            corrected_word = suggestions[0] if suggestions else word
            corrected_words.append(corrected_word)
        return ' '.join(corrected_words)