from .spacy_helper import parse_query
from deeppavlov_models import BertModel

from SPARQLWrapper import SPARQLWrapper, JSON
import json
import requests
import pandas as pd

MAX_ATTEMPT = 3

dbpedia_sparql_endpoint = SPARQLWrapper(
    "https://dbpedia.org/sparql", agent="TeamsBot"
)
wikidata_sparql_endpoint = SPARQLWrapper(
    "https://query.wikidata.org/sparql", agent="TeamsBot"
)

class DbpediaBot:
    def get_answer(self, query):
        answer = dict()

        properties_found, properties = self.find_wikidata_properties(query)
        entities_found, entities_data = self.get_entities_data(query)

        if entities_found:
            answer.update({ "entities": entities_data })

            context = [ data["abstract"] for entity, data in entities_data.items() ]
            question = [ query ] * len(context)
            model = BertModel(context, question)
            prediction = model.make_prediction()

            answer.update({ "bert": prediction })

            if properties_found:
                properties_linked, properties_data = self.get_properties_data(
                    query, properties, entities_data
                )
                if properties_linked:
                    answer.update({ "wikidata": properties_data })

        return answer

    def find_wikidata_properties(self, query):
        properties = list()
        subjects, objects, relations = parse_query(query)
        triple = { **subjects, **objects, **relations }

        print("Query properties:", triple)
        data = pd.read_json(
            r'/Users/mikhbych/Projects/teams-bot/dbpedia/properties.json'
        )

        for _, text in triple.items():
            properties.extend(data.loc[(data["text"] == text)]["code"].values)

        properties_found = bool(properties)
        return properties_found, properties

    def get_entities_data(self, query):
        entities_data = dict()
        subjects, objects, relations = parse_query(query)
        entities = { **subjects, **objects }

        for _, entity  in entities.items():
            entity_found = self.link_entity_dbpedia(
                entity, entities_data, dbpedia_sparql_endpoint
            )

        entities_found = bool(entities) and bool(entities_data)
        return entities_found, entities_data

    def link_entity_dbpedia(self, entity, entities_data, sparql_endpoint):
        for attempt in range(MAX_ATTEMPT):
            entity_linked, data = self.dbpedia_abstract_query(sparql_endpoint, entity, attempt)
            if entity_linked:
                entities_data[entity] = data
                break

        return entity_linked

    def dbpedia_abstract_query(self, sparql_endpoint, entity, attempt):
        if attempt == 0:
            query = self.form_sparql_request_abstract_v1(entity)
            response = self.send_sparql_request(query, sparql_endpoint)
            print("-----------------\n")

            print("dbpedia_abstract_query v1")

            print(entity)
            print(response)
            print("-----------------\n")
            response_status = len(response["results"]["bindings"]) > 0

        if attempt == 1:
            query = self.form_sparql_request_abstract_v2(entity)
            response = self.send_sparql_request(query, sparql_endpoint)
            print("-----------------\n")

            print("dbpedia_abstract_query v2")

            print(entity)
            print(response)
            print("-----------------\n")
            response_status = len(response["results"]["bindings"]) > 0

        if attempt == 2:
            query = self.form_sparql_request_abstract_v3(entity)
            response = self.send_sparql_request(query, sparql_endpoint)
            print("-----------------\n")

            print("dbpedia_abstract_query v3")

            print(entity)
            print(response)
            print("-----------------\n")
            response_status = len(response["results"]["bindings"]) > 0

        result = self.convert_sparql_response(response, entity)
        return response_status, result

    def send_sparql_request(self, query, sparql_endpoint):
        sparql_endpoint.setQuery(query)
        sparql_endpoint.setReturnFormat(JSON)
        response = sparql_endpoint.query().convert()
        return response

    def convert_sparql_response(self, response, entity):
        result = dict()

        if bool(response["results"]["bindings"]):
            data = response["results"]["bindings"][0]
            result = { key: value["value"] for key, value in data.items() }

        return result

    def form_sparql_request_abstract_v1(self, entity):
        entity_label = entity.capitalize()

        print(entity_label)

        query = (
            """
                SELECT DISTINCT ?type ?entity ?abstract ?thumbnail
                WHERE
                {
                    {
                        ?entity rdfs:label            ?label;
                                dbo:abstract          ?abstract.
                        ?alias  dbo:wikiPageRedirects ?entity;
                                rdfs:label            \"""" + entity_label + """\"@en.
                        FILTER(LANG(?label) = "en")
                    }
                    UNION
                    {
                        ?entity rdfs:label   ?label;
                                dbo:abstract ?abstract;
                                rdf:type     yago:Matrix108267640.
                        FILTER(LANG(?label) = "en")
                        FILTER(STRSTARTS(?label, \"""" + entity_label + """\"))

                    }
                    UNION
                    {
                        ?entity rdfs:label   ?label;
                                dbo:abstract ?abstract;
                                rdf:type     yago:Polynomial105861855.
                        FILTER(LANG(?label) = "en")
                        FILTER(STRSTARTS(?label, \"""" + entity_label + """\"))

                    }
                    UNION
                    {
                        ?entity rdfs:label   ?label;
                                dbo:abstract ?abstract;
                                rdf:type     yago:Function113783816.
                        FILTER(LANG(?label) = "en")
                        FILTER(STRSTARTS(?label, \"""" + entity_label + """\"))

                    }
                    UNION
                    {
                        ?entity rdfs:label   ?label;
                                dbo:abstract ?abstract;
                                rdf:type     yago:Vector105864577.
                        FILTER(LANG(?label) = "en")
                        FILTER(STRSTARTS(?label, \"""" + entity_label + """\"))

                    }
                    UNION
                    {
                        ?entity rdfs:label   ?label;
                                dbo:abstract ?abstract;
                                rdf:type     yago:ProgrammingLanguage106898352.
                        FILTER(LANG(?label) = "en")
                        FILTER(STRSTARTS(?label, \"""" + entity_label + """\"))
                    }
                    UNION
                    {
                        ?entity rdfs:label   ?label;
                                dbo:abstract ?abstract;
                                rdf:type     yago:DataStructure105728493.
                        FILTER(LANG(?label) = "en")
                        FILTER(STRSTARTS(?label, \"""" + entity_label + """\"))

                    }
                    UNION
                    {
                        ?entity rdfs:label   ?label;
                                dbo:abstract ?abstract;
                                rdf:type     yago:Algorithm105847438.
                        FILTER(LANG(?label) = "en")
                        FILTER(STRSTARTS(?label, \"""" + entity_label + """\"))

                    }
                    OPTIONAL
                    {
                        ?entity dbo:thumbnail         ?thumbnail.

                    }
                    FILTER(LANG(?abstract) = "en")
                }
                LIMIT 10
            """
        )

        return query

    def form_sparql_request_abstract_v2(self, entity):
        entity_label = entity.capitalize() + " "

        query = (
            """
                SELECT DISTINCT ?entity ?abstract ?thumbnail
                WHERE
                {
                    {
                        ?entity rdfs:label            ?label;
                                dbo:abstract          ?abstract.
                        ?alias  dbo:wikiPageRedirects ?entity;
                                rdfs:label            \"""" + entity_label + """\"@en.
                        FILTER(LANG(?label) = "en")
                    }
                    UNION
                    {
                        ?entity rdfs:label   ?label;
                                dbo:abstract ?abstract;
                                rdf:type     yago:ProgrammingLanguage106898352.
                        FILTER(LANG(?label) = "en")
                        FILTER(STRSTARTS(?label, \"""" + entity_label + """\"))

                    }
                    UNION
                    {
                        ?entity rdfs:label   ?label;
                                dbo:abstract ?abstract;
                                rdf:type     yago:DataStructure105728493.
                        FILTER(LANG(?label) = "en")
                        FILTER(STRSTARTS(?label, \"""" + entity_label + """\"))
                    }
                    UNION
                    {
                        ?entity rdfs:label   ?label;
                                dbo:abstract ?abstract;
                                rdf:type     yago:Algorithm105847438.
                        FILTER(LANG(?label) = "en")
                        FILTER(STRSTARTS(?label, \"""" + entity_label + """\"))
                    }
                    OPTIONAL
                    {
                        ?entity dbo:thumbnail         ?thumbnail.
                        ?entity a ?type
                    }
                    FILTER(LANG(?abstract) = "en")
                }

                LIMIT 10
            """
        )

        return query

    def form_sparql_request_abstract_v3(self, entity):
        entity_label = entity.capitalize()

        query = (
            """
                SELECT DISTINCT ?entity ?abstract ?thumbnail
                WHERE
                {
                    {
                        ?entity rdfs:label            ?label;
                                dbo:abstract          ?abstract.
                        ?alias  dbo:wikiPageRedirects ?entity;
                                rdfs:label            \"""" + entity_label + """\"@en.
                        FILTER(LANG(?label) = "en")
                    }
                    UNION
                    {
                        ?entity rdfs:label   \"""" + entity_label + """\"@en;
                                dbo:abstract ?abstract.
                    }
                    OPTIONAL
                    {
                        ?entity dbo:thumbnail ?thumbnail.
                        ?entity rdf:type      dbo:Software.

                    }
                    FILTER(LANG(?abstract) = "en")
                }
                LIMIT 10
            """
        )

        return query

    def get_properties_data(self, query, properties, entities_data):
        properties_data = dict()

        for property in properties:
            for entity in entities_data:
                property_linked, result = self.wikidata_property_query(
                    entity, property, wikidata_sparql_endpoint
                )
                if property_linked:
                    properties_data[entity] = result

        properties_linked = bool(properties_data)

        return properties_linked, properties_data

    def wikidata_property_query(self, entity, property, sparql_endpoint):
        entity_label = entity.lower()

        query = (
            """
                SELECT ?entity ?property_id
                WHERE
                {
                    ?entity rdfs:label               \"""" + entity_label + """\"@en;
                            wdt:""" + property + """ ?property_id.
                }
                LIMIT 10
            """
        )

        response = self.send_sparql_request(query, sparql_endpoint)
        response_status = len(response["results"]["bindings"]) > 0

        result = self.convert_sparql_response(response, entity)

        return response_status, result
