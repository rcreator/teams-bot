import os

class AppConfig:

    PORT = 3978
    APP_ID = os.environ.get("MicrosoftAppId", "0f405b83-8b6b-4f97-86e5-2a7753c73bb2")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "520x1oVD1Wo7R_MFH.V6U8j-_u85H~Hge2")
