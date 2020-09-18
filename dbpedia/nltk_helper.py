import nltk

nltk.download("averaged_perceptron_tagger")
nltk.download("maxent_ne_chunker")
nltk.download("words")

PROPERTY_TAGS = [ "NN", "NNP", "NNPS", "NNS" ]

def pos_tagger(user_query, properties):
    tokens = nltk.word_tokenize(user_query)
    pos_tags = nltk.pos_tag(tokens)

    # Save all tokens that can be used as properties in SPARQL query
    # Suitable tags : 'NN', 'NNP', 'NNPS', 'NNS'
    # Also don't forget to process composite tokens

    for token, pos_tag in pos_tags:
        if pos_tag in PROPERTY_TAGS:
            properties.append(" ".join(token.split("-")))

    return pos_tags


def get_entities_and_properties(user_query):
    properties, named_entities = [], []

    pos_tags = pos_tagger(user_query, properties)
    chunks = nltk.ne_chunk(pos_tags, binary=True)

    cur_chunk = []
    for chunk in chunks:
        if hasattr(chunk, "label") and chunk.label:
            cur_chunk.append(
                " ".join([token for token, _ in chunk.leaves()])
            )
            if cur_chunk:
                entity = " ".join(cur_chunk)
                if entity not in named_entities:
                    cur_chunk = []
                    named_entities.append(entity)

    return named_entities, properties
