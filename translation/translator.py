import requests
import uuid
from config import AppConfig
from googletrans import Translator

class TranslatorM:
    def __init__(self, config: AppConfig):
        self.subscription_key = config.SUBSCRIPTION_KEY
        self.subscription_region = config.SUBSCRIPTION_REGION

    async def translate(self, input_question, output_lang):
        translator = Translator()

        try:
            result = translator.translate(input_question, dest=output_lang)
            return result.text
        except Exception as exception:
            base_url = "https://api.cognitive.microsofttranslator.com"
            path = "/translate?api-version=3.0"
            params = "&to=" + output_lang
            url = base_url + path + params

            headers = {
                "Ocp-Apim-Subscription-Key": self.subscription_key,
                "Ocp-Apim-Subscription-Region": self.subscription_region,
                "Content-type": "application/json",
                "X-ClientTraceId": str(uuid.uuid4()),
            }
            body = [{ "text": input_question }]

            response = requests.post(url, headers=headers, json=body)
            if response.status_code / 100 != 2:
                return "Unable to translate text. Check your subscription key and region."

            return json_response[0]["translations"][0]["text"]
