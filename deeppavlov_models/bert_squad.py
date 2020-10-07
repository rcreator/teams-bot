import requests

API_ENDPOINT = "http://127.0.0.1:5005/model"

class BertModel:
    def make_prediction(self, context, question):
        PARAMS = { "context_raw":  context,
                   "question_raw": [ question ] * len(context)}

        response = requests.post(url=API_ENDPOINT, json=PARAMS)
        response = response.json()

        max_score = 0
        correct_answer = ""

        for answer, _, _, score in response:
            if max_score < score:
                max_score = score
                correct_answer = answer

        return correct_answer
