from botbuilder.core import (
    CardFactory, TurnContext, MessageFactory, UserState, ConversationState,
)
from botbuilder.core.teams import (
    TeamsActivityHandler, TeamsInfo,
)
from botbuilder.ai.qna import QnAMaker, QnAMakerEndpoint

from config import AppConfig
from translation.settings import TranslatorSettings
from dbpedia import DbpediaBot

MAX_CONF_SCORE = 0.95

class TeamsQABot(TeamsActivityHandler):
    def __init__(self, config: AppConfig,
                       user_state: UserState,
                       conv_state: ConversationState):

        """self.qna_maker = QnAMaker(
            QnAMakerEndpoint(
                knowledge_base_id=config.QNA_KNOWLEDGEBASE_ID,
                endpoint_key=config.QNA_ENDPOINT_KEY,
                host=config.QNA_ENDPOINT_HOST
            )и
        )"""

        self.user_state = user_state
        self.conv_state = conv_state
        self.language_preference_accessor = self.user_state.create_property(
            "LanguagePreference"
        )

    async def on_message_activity(self, turn_context: TurnContext):
        qna_answered = False

        """
        response = await self.qna_maker.get_answers(turn_context)
        if response and len(response) > 0:
            if response[0].score >= MAX_CONF_SCORE:
                qna_answered = True
                await turn_context.send_activity(
                     MessageFactory.text(response[0].answer)
                )

         """
        if not qna_answered:
            query = turn_context.activity.text.strip()

            print("Translated question:", query)

            await turn_context.send_activity("No QnA Maker answers were found. " +
                                             "Connecting to Dbpedia, just wait...")

            helper = DbpediaBot()
            response = helper.get_answer(query)

            dp_ans = ""

            if "data" in response.keys():
                if "bert" in response["data"].keys():
                    dp_ans = response["data"]["answer"]
                if "entities" in response["data"].keys():
                    for entity in response["data"]["entities"]:
                        answer = "\n\n".join([response["data"]["entities"][key]["abstract"]
                            for key in response["data"]["entities"].keys()])
                if "wikidata" in response["data"].keys():
                    for entity in response["data"]["properties"]:
                        answer = "\n\n".join([response["data"]["properties"][key]["property_id"]
                            for key in response["data"]["properties"].keys()])
            else:
                answer = ("I can't answer this question. " +
                          "Please try to specify it as accurately as possible.")

            await turn_context.send_activity(dp_ans + "\n\n" + answer)
