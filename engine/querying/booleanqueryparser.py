from . import AndQuery, OrQuery, QueryComponent, TermLiteral, PhraseLiteral
from engine.text import Preprocessing

class BooleanQueryParser:
    class _StringBounds:
        def __init__(self, start : int, length : int):
            self.start = start
            self.length = length

    class _Literal:
        def __init__(self, bounds : 'BooleanQueryParser._StringBounds', literal_component : QueryComponent):
            self.bounds = bounds
            self.literal_component = literal_component

    @staticmethod
    def _find_next_subquery(query : str, start_index : int) -> _StringBounds:
        length_out = 0

        # Find the start of the next subquery by skipping spaces and + signs.
        test = query[start_index]
        while test == ' ' or test == '+':
            start_index += 1
            test = query[start_index]

        # Find the end of the next subquery.
        next_plus = query.find("+", start_index + 1)
        if next_plus < 0:
            # If there is no other + sign, then this is the final subquery in the
            # query string.
            length_out = len(query) - start_index
        else:
            # If there is another + sign, then the length of this subquery goes up
            # to the next + sign.
        
            # Move next_plus backwards until finding a non-space non-plus character.
            test = query[next_plus]
            while test == ' ' or test == '+':
                next_plus -= 1
                test = query[next_plus]

            length_out = 1 + next_plus - start_index

        # startIndex and lengthOut give the bounds of the subquery.
        return BooleanQueryParser._StringBounds(start_index, length_out) 
            
    @staticmethod
    def _find_next_literal(subquery: str, start_index: int, preprocess: Preprocessing) -> 'BooleanQueryParser._Literal':
        sub_length = len(subquery)
        length_out = 0

        # Skip past white space.
        while start_index < sub_length and subquery[start_index] == ' ':
            start_index += 1

        # Check if this is a phrase literal
        if start_index < sub_length and subquery[start_index] == '"':
            next_quote = subquery.find('"', start_index + 1)
            if next_quote >= 0:
                phrase_contents = subquery[start_index + 1:next_quote]
                phrase_contents = preprocess.process(phrase_contents)
                length_out = next_quote - start_index + 1 

                # Modification: Check if phrase_contents contain more than one word
                if ' ' in phrase_contents:
                    phrase_literals = BooleanQueryParser.parse_query(phrase_contents, preprocess)

                    return BooleanQueryParser._Literal(
                        BooleanQueryParser._StringBounds(start_index, length_out),
                        PhraseLiteral(phrase_literals.components)  # Keep as PhraseLiteral
                    )
                else:
                    # Modification: Create a TermLiteral instead of a PhraseLiteral for single word in quotes
                    return BooleanQueryParser._Literal(
                        BooleanQueryParser._StringBounds(start_index, length_out),
                        TermLiteral(phrase_contents)
                    )

            else:
                # This is a malformed phrase missing a second quotation mark. 
                # For malformed phrases, consider the whole string until the next space or the end as literal.
                next_space = subquery.find(' ', start_index)
                end_index = next_space if next_space >= 0 else sub_length
                malformed_contents = subquery[start_index:end_index]
                # Using TermLiteral instead of PhraseLiteral for malformed phrases
                return BooleanQueryParser._Literal(
                    BooleanQueryParser._StringBounds(start_index, end_index - start_index),
                    TermLiteral(malformed_contents)
                )

        # If not a phrase literal, locate the next space to find the end of this literal.
        next_space = subquery.find(' ', start_index)
        if next_space < 0:
            length_out = sub_length - start_index
        else:
            length_out = next_space - start_index
        
        term = preprocess.process(subquery[start_index:start_index + length_out])
     
        return BooleanQueryParser._Literal(
            BooleanQueryParser._StringBounds(start_index, length_out),
            TermLiteral(term)
        )

    @staticmethod
    def parse_query(query : str, preprocess: Preprocessing) -> QueryComponent:
        all_subqueries = []
        start = 0

        while True:
            # Identify the next subquery: a portion of the query up to the next + sign.
            next_subquery = BooleanQueryParser._find_next_subquery(query, start)
            # Extract the identified subquery into its own string.
            subquery = query[next_subquery.start:next_subquery.start + next_subquery.length]
            sub_start = 0

            # Store all the individual components of this subquery.
            subquery_literals = []

            while True:
                # Extract the next literal from the subquery.
                lit = BooleanQueryParser._find_next_literal(subquery, sub_start, preprocess)

                # Add the literal component to the conjunctive list.
                subquery_literals.append(lit.literal_component)

                # Set the next index to start searching for a literal.
                sub_start = lit.bounds.start + lit.bounds.length
                if sub_start >= len(subquery):
                    break

            # After processing all literals, we are left with a conjunctive list
            # of query components, and must fold that list into the final disjunctive list
            # of components.
            
            # If there was only one literal in the subquery, we don't need to AND it with anything --
            # its component can go straight into the list.
            if len(subquery_literals) == 1:
                all_subqueries.append(subquery_literals[0])
            else:
                # With more than one literal, we must wrap them in an AndQuery component.
                all_subqueries.append(AndQuery(subquery_literals))
          
            start = next_subquery.start + next_subquery.length
            if start >= len(query):
                break
        
        # After processing all subqueries, we either have a single component or multiple components
        # that must be combined with an OrQuery.
        if len(all_subqueries) == 1:
            return all_subqueries[0]
        elif len(all_subqueries) > 1:
            return OrQuery(all_subqueries)
        else:
            return None
