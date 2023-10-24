from engine.text import Preprocessing
import math
class RankedQuery:
    #define Ranked Querying here.
    def parse_query(query: str, preprocess: Preprocessing):
        # Get each term in the query
        proc_query = preprocess.process(query)
        terms = proc_query.split(' ')
        for term in terms:
            #Find N (number of documents) and dft (document frequency of term).
            #wqt = math.log(1 + (N/dft))
            pass