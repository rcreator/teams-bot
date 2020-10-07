import re
import spacy
from spacy.tokens import Token, Span
from spacy.tokenizer import Tokenizer
from spacy.matcher import Matcher

from spacy.lang.char_classes import (
    ALPHA, ALPHA_LOWER, ALPHA_UPPER,
    CONCAT_QUOTES, LIST_ELLIPSES, LIST_ICONS
)

from spacy.util import (
    compile_prefix_regex, compile_infix_regex, compile_suffix_regex
)

QUESTION_KEYS = [
    "what",
    "which",
    "how",
    "why",
    "when",
    "where",
    "who",
]

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

MATCHER = Matcher(nlp.vocab)
RELATION_PATTERN = [ {'DEP':'ROOT'},
                     {'DEP':'prep' , 'OP':"?"},
                     {'DEP':'agent', 'OP':"?"},
                     {'POS':'ADJ'  , 'OP':"?"} ]

def extract_noun_chunks(doc, dep_tag):
    chunks = {}

    for chunk in doc.noun_chunks:
        if chunk.root.dep_.find(dep_tag) == True and chunk.root.text not in QUESTION_KEYS:
            start = (chunk[0].dep_ == "det")
            chunks[chunk.root.dep_] = (chunk[start:].text)

    return chunks

def extract_entities(doc, dep_tag):
    entities = {}

    for token in doc:
        if token.dep_ != "punct":
            if token.dep_.find(dep_tag) == True and token.text not in QUESTION_KEYS:
                entities[token.dep_] = token.text
                for child in token.children:
                    if (child.dep_.endswith("compound") == True or
                        child.dep_.endswith("mod") == True or
                        child.dep_.endswith("poss") == True or
                        child.dep_.endswith("attr") == True):
                        entities[token.dep_] = child.text + " " + entities[token.dep_]

    return entities

def extract_nouns(doc):
    subject = ""

    prev_token_dep = ""
    prev_token_text = ""

    prefix = ""
    modifier = ""

    for token in doc:
        if token.dep_ != "punct":
            if token.dep_.find("compound") == True:
                prefix = token.text
                if prev_token_dep.find("compound") == True:
                    prefix = prev_token_text + " " + token.text

            if token.dep_.endswith("mod") == True:
                modifier = token.text
                if prev_token_dep.find("compound") == True:
                    modifier = prev_token_text + " " + token.text

            if token.pos_ == "NOUN":
                if modifier and prefix:
                    subjects = modifier + " " + prefix + " " + token.text
                elif modifier:
                    subject = modifier + " " + token.text
                elif prefix:
                    subject = prefix + " " + token.text
                else:
                    subject = token.text

                prefix = ""
                modifier = ""
                prev_token_dep = ""
                prev_token_text = ""

            prev_token_dep = token.dep_
            prev_token_text = token.text

    return { "subj": subject.strip() }

def extract_relation(doc):
    MATCHER.add("RelationMatching", None, RELATION_PATTERN)

    matches = MATCHER(doc)
    span = doc[matches[-1][1]:matches[-1][2]]

    return { 'ROOT' : span.text }

def parse_query(user_query):
    doc = nlp(user_query)

    subjects = extract_noun_chunks(doc, "subj")
    objects = extract_noun_chunks(doc, "obj")
    relations = extract_relation(doc)

    if not (bool(subjects) or bool(objects)):
        subjects.update(extract_entities(doc, "subj"))
        objects.update(extract_entities(doc, "obj"))

    if not (bool(subjects) or bool(objects)):
        subjects = extract_nouns(doc)

        if subjects["subj"] == "":
            subjects = relations

    return subjects, objects, relations
