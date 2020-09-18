import re
import spacy
from spacy.tokens import Token
from spacy.tokenizer import Tokenizer
from spacy.lang.char_classes import ALPHA, ALPHA_LOWER, ALPHA_UPPER, CONCAT_QUOTES, LIST_ELLIPSES, LIST_ICONS
from spacy.util import compile_prefix_regex, compile_infix_regex, compile_suffix_regex

PROPERTY_POS = [ "PROPN", "NOUN" ]
PROPERTY_TAGS = [ "NN", "NNP", "NNPS", "NNS" ]

def custom_tokenizer(nlp):
    infixes = (
        LIST_ELLIPSES
        + LIST_ICONS
        + [
            r"(?<=[0-9])[+\-\*^](?=[0-9-])",
            r"(?<=[{al}{q}])\.(?=[{au}{q}])".format(
                al=ALPHA_LOWER, au=ALPHA_UPPER, q=CONCAT_QUOTES
            ),
            r"(?<=[{a}]),(?=[{a}])".format(a=ALPHA),
            r"(?<=[{a}0-9])[:<>=/](?=[{a}])".format(a=ALPHA)
        ]
    )

    infix_re = compile_infix_regex(infixes)

    return Tokenizer(nlp.vocab, prefix_search=nlp.tokenizer.prefix_search,
                                suffix_search=nlp.tokenizer.suffix_search,
                                infix_finditer=infix_re.finditer,
                                token_match=nlp.tokenizer.token_match,
                                rules=nlp.Defaults.tokenizer_exceptions)

nlp = spacy.load("en_core_web_sm")
nlp.tokenizer = custom_tokenizer(nlp)

def extract_subjects(doc):
    subjects = {}

    for token in doc:
        if token.dep_ != "punct":
            if token.dep_.find("subj") == True:
                subjects[token.dep_] = token.text
                for child in token.children:
                    if (child.dep_ == "compound" or
                        child.dep_.endswith("mod") or
                        child.dep_ == "poss"):
                        subjects[token.dep_] = child.text + " " + subjects[token.dep_]

    return subjects

def extract_objects(doc):
    objects = {}

    for token in doc:
        if token.dep_ != "punct":
            if token.dep_.find("obj") == True:
                objects[token.dep_] = token.text
                for child in token.children:
                    if (child.dep_ == "compound" or
                        child.dep_.endswith("mod") or
                        child.dep_ == "poss"):
                        objects[token.dep_] = child.text + " " + objects[token.dep_]

    return objects

def extract_relations(doc):
    root = [token for token in doc if token.head == token][0]
    return { root.dep_: root.text }

def get_entities(user_query):
    doc = nlp(user_query)
    return [(token.text, token.label_) for token in doc.ents]

def get_triples(user_query):
    doc = nlp(user_query)

    subjects = extract_subjects(doc)
    objects = extract_objects(doc)
    relations = extract_relations(doc)

    return subjects, objects, relations
