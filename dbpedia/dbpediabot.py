from SPARQLWrapper import SPARQLWrapper, JSON

from .spacy_helper import get_triples, get_entities

QUESTION_KEYS = [
    ( "What", "what" ),
    ( "Which", "which" ),
    ( "How", "how" ),
    ( "Why", "why" ),
    ( "When", "when" ),
    ( "Where", "where" ),
    ( "Who", "who" )
]

class DbpediaBot:
    def get_answer(self, query):
        print(query)

        named_entities = get_entities(query)

        print("named entities list:", named_entities)

        subjects, objects, relations = get_triples(query)

        print("subjects:", subjects)
        print("objects:", objects)
        print("relations:", relations)
