import os

# Fill in variable values with your Azure resource's data

DEFAULT_APP_ID = ""
DEFAULT_APP_PASSWORD = ""

DEFAULT_QNA_KNOWLEDGEBASE_ID = ""
DEFAULT_QNA_ENDPOINT_KEY = ""
DEFAULT_QNA_ENDPOINT_HOST = ""

DEFAULT_SUBSCRIPTION_KEY = ""
DEFAULT_SUBSCRIPTION_REGION = ""

class AppConfig:
    PORT = 3978

    APP_ID = os.environ.get("MicrosoftAppId", DEFAULT_APP_ID)
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", DEFAULT_APP_PASSWORD)

    QNA_KNOWLEDGEBASE_ID = os.environ.get("QnAKnowledgebaseId", DEFAULT_QNA_KNOWLEDGEBASE_ID)
    QNA_ENDPOINT_KEY = os.environ.get("QnAEndpointKey", DEFAULT_QNA_ENDPOINT_KEY)
    QNA_ENDPOINT_HOST = os.environ.get("QnAEndpointHostName", DEFAULT_QNA_ENDPOINT_HOST)

    SUBSCRIPTION_KEY = os.environ.get("SubscriptionKey", DEFAULT_SUBSCRIPTION_KEY)
    SUBSCRIPTION_REGION = os.environ.get("SubscriptionRegion", DEFAULT_SUBSCRIPTION_REGION)
