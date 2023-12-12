import math

class RankedQuery:
    def __init__(self, index):
        self.index = index
        self.total_docs = self.index.get_total_docs()
        self.avg_doc_length = self.index.calculate_average_document_length()
        self.ld = self.index.get_doc_weights()

    def calculate_wqt(self, term):
        df = len(self.index.getPostings(term))
        wqt = math.log(1+(self.total_docs/df))
        print(f"Term: '{term}', df: {df}, wqt: {wqt}")
        return wqt

    def calculate_wdt(self, term, doc_id, doc_length):
        tf = self.index.get_term_frequency(term, doc_id)
        print("Term Freq: " + str(tf))
        wdt = 1 + math.log(tf)
        print(f"Term: '{term}', Doc ID: {doc_id}, tf: {tf}, wdt: {wdt}")
        return wdt

    def rank_documents(self, query, postings):
        term = query.term
        accumulators = {}
        doc_lengths = self.index.get_doc_weights() 
        
        wqt = self.calculate_wqt(term)
        postings = self.index.getPostings(term)
        
        for posting in postings:
            doc_id = posting.doc_id
            L_d = self.ld.get(doc_id, 1)
            doc_length = doc_lengths.get(doc_id, self.avg_doc_length) 
            print("Doc Length: " + str(doc_length))
            wdt = self.calculate_wdt(term, doc_id, doc_length)
            if doc_id not in accumulators:
                accumulators[doc_id] = 0 
            accumulators[doc_id] += (wqt * wdt) / L_d

            print(f"Updating score for Doc ID {doc_id}: New Score: {accumulators[doc_id]}")

        # Sort documents by score in descending order
        ranked_documents = sorted(accumulators.items(), key=lambda item: item[1], reverse=True)
        return ranked_documents

    def search(self, query_terms):
        ranked_documents = self.rank_documents(query_terms)
        for doc_id, score in ranked_documents[:10]:  # Get top 10 documents
            doc_title = self.index.get_document_title(doc_id)
            print(f"Document ID: {doc_id}, Title: {doc_title}, Score: {score:.3f}")