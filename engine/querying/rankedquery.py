import math

class RankedQuery:
    def __init__(self, index):
        self.index = index
        self.total_docs = self.index.get_total_documents()
        self.avg_doc_length = self.index.calculate_average_doc_length()
        self.ld = self.index.get_doc_weights()

    def calculate_wqt(self, term, use_okapi):
        df = len(self.index.getPostings(term))
        if use_okapi:
            wqt = max(0.1, math.log((self.total_docs - df + 0.5) / (df + 0.5)))
        else:
            wqt = math.log(1+(self.total_docs/df))
        return wqt

    def calculate_wdt(self, term, doc_id, use_okapi):
        tf = self.index.get_term_frequency(term, doc_id)
        doc_tokens = self.index.get_document_length(doc_id)
        if use_okapi:
            wdt = (2.2 * tf / (1.2*(0.25 + 0.75 * (doc_tokens / self.avg_doc_length)) + tf))
        else:
            wdt = 1 + math.log(tf)
        return wdt

    def rank_documents(self, raw_query, use_okapi):
        # Preprocess the query to split it into individual terms
        terms = self.preprocess_query(raw_query)
        
        accumulators = {}
        doc_lengths = self.index.get_doc_weights()

        for term in terms:
            wqt = self.calculate_wqt(term, use_okapi)
            postings = self.index.getPostings(term)

            for posting in postings:
                doc_id = posting.doc_id
                wdt = self.calculate_wdt(term, doc_id, use_okapi)

                if use_okapi:
                    L_d = 1
                else:
                    L_d = self.ld.get(doc_id, 1)

                if doc_id not in accumulators:
                    accumulators[doc_id] = 0 
                accumulators[doc_id] += (wqt * wdt) / L_d

        # Sort documents by score in descending order
        ranked_documents = sorted(accumulators.items(), key=lambda item: item[1], reverse=True)
        return ranked_documents

    def preprocess_query(self, raw_query):
        processed_terms = raw_query.lower().split()  
        return processed_terms