from typing import List
from botbuilder.core import (
    CardFactory, TurnContext, MessageFactory, UserState
)
from botbuilder.core.teams import TeamsActivityHandler, TeamsInfo
from botbuilder.schema import CardAction, HeroCard, Mention, ConversationParameters
from botbuilder.schema.teams import TeamInfo, TeamsChannelAccount
from botbuilder.schema._connector_client_enums import ActionTypes
from botbuilder.ai.qna import QnAMaker, QnAMakerEndpoint

from config import AppConfig
from translation.settings import TranslatorSettings
from dbpedia import DbpediaBot

MAX_CONF_SCORE = 0.95

class TeamsQABot(TeamsActivityHandler):
    def __init__(self, config: AppConfig, user_state: UserState):
        self.qna_maker = QnAMaker(
            QnAMakerEndpoint(
                knowledge_base_id=config.QNA_KNOWLEDGEBASE_ID,
                endpoint_key=config.QNA_ENDPOINT_KEY,
                host=config.QNA_ENDPOINT_HOST
            )
        )
        self.user_state = user_state
        self.language_preference_accessor = self.user_state.create_property(
            "LanguagePreference"
        )

    async def on_message_activity(self, turn_context: TurnContext):
        response = await self.qna_maker.get_answers(turn_context)

        if response and len(response) > 0:
            if response[0].score >= MAX_CONF_SCORE:

                # If FAQ question: provide answer using QnAMaker KB

                print(response[0].score)
                await turn_context.send_activity(MessageFactory.text(response[0].answer))

        helper = DbpediaBot()
        query = turn_context.activity.text.strip()
        helper.get_answer(query)

        await turn_context.send_activity("No QnA Maker answers were found.")
