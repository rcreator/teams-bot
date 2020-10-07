import sys
from datetime import datetime
import traceback

from flask import Flask, request, Response
from http import HTTPStatus
import asyncio

from botbuilder.core import (
    TurnContext,
    BotFrameworkAdapterSettings,
    BotFrameworkAdapter,
    MemoryStorage,
    UserState,
    ConversationState
)
from botbuilder.schema import Activity, ActivityTypes

from config import AppConfig
from translation import TranslatorMiddleware, TranslatorM
from bots import TeamsQABot

CONFIG = AppConfig()
SETTINGS = BotFrameworkAdapterSettings(CONFIG.APP_ID, CONFIG.APP_PASSWORD)
ADAPTER = BotFrameworkAdapter(SETTINGS)

# Catch-all for errors.
async def on_error(context: TurnContext, error: Exception):
    # This check writes out errors to console log .vs. app insights.
    # NOTE: In production environment, you should consider logging this to Azure
    #       application insights.
    print(f"\n [on_turn_error] unhandled error: {error}", file=sys.stderr)

    # Send a message to the user
    await context.send_activity("The bot encountered an error or bug.")
    await context.send_activity("To continue to run this bot, please fix the bot source code.")
    # Send a trace activity if we're talking to the Bot Framework Emulator
    if context.activity.channel_id == 'emulator':
        # Create a trace activity that contains the error object
        trace_activity = Activity(
            label="TurnError",
            name="on_turn_error Trace",
            timestamp=datetime.utcnow(),
            type=ActivityTypes.trace,
            value=f"{error}",
            value_type="https://www.botframework.com/schemas/error"
        )
        # Send a trace activity, which will be displayed in Bot Framework Emulator
        await context.send_activity(trace_activity)

ADAPTER.on_turn_error = on_error

MEMORY_STORAGE = MemoryStorage()
USER_STATE = UserState(MEMORY_STORAGE)
CONVERSATION_STATE = ConversationState(MEMORY_STORAGE)

TRANSLATOR = TranslatorM(CONFIG)
TRANSLATOR_MIDDLEWARE = TranslatorMiddleware(TRANSLATOR, USER_STATE)
ADAPTER.use(TRANSLATOR_MIDDLEWARE)

BOT = TeamsQABot(CONFIG, USER_STATE, CONVERSATION_STATE)

LOOP = asyncio.get_event_loop()
app = Flask(__name__)

@app.route("/api/messages", methods=["POST"])
def messages():
    if "application/json" in request.headers["Content-Type"]:
        message_body = request.json
    else:
        return Response(status=HTTPStatus.UNSUPPORTED_MEDIA_TYPE)

    activity = Activity().deserialize(message_body)
    if "Authorization" in request.headers:
        auth_header = request.headers["Authorization"]
    else:
        auth_header = ""

    try:
        task = LOOP.create_task(ADAPTER.process_activity(activity, auth_header, BOT.on_turn))
        LOOP.run_until_complete(task)
        return Response(status=HTTPStatus.OK)
    except Exception as exception:
        raise exception

if __name__ == "__main__":
    try:
        app.run(debug=False, host="localhost", port=CONFIG.PORT)
    except Exception as error:
        raise error
