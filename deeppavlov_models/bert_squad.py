import requests

API_ENDPOINT = "http://127.0.0.1:5005/model"

class BertModel:
    def __init__(self, context, question, endpoint=API_ENDPOINT):
        self.context = context
        self.question = question
        self.endpoint = endpoint

    def make_prediction(self):
        PARAMS = { "context_raw":  self.context,
                   "question_raw": self.question }

        response = requests.post(url=self.endpoint, json=PARAMS)
        response = response.json()

        max_score = 0
        correct_answer = ""
        for answer, _, _, score in response:
            if max_score < score:
                max_score = score
                correct_answer = answer

        return correct_answer
