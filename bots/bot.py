from botbuilder.schema import (
    ActionTypes, Attachment, HeroCard, CardAction, CardImage, ChannelAccount,
)
from botbuilder.core import (
    CardFactory, TurnContext, MessageFactory, UserState, ConversationState,
)
from botbuilder.core.teams import (
    TeamsActivityHandler, TeamsInfo,
)
from botbuilder.ai.qna import QnAMaker, QnAMakerEndpoint

from config import AppConfig
from translation.settings import TranslatorSettings
from dbpedia import DBpediaBot
from deeppavlov_models import BertModel
from googletrans import Translator

translator = Translator()

MAX_CONF_SCORE = 0.95

class TeamsQABot(TeamsActivityHandler, DBpediaBot, BertModel):
    def __init__(self, config: AppConfig,
                       user_state: UserState,
                       conv_state: ConversationState):

        self.qna_maker = QnAMaker(
            QnAMakerEndpoint(
                knowledge_base_id=config.QNA_KNOWLEDGEBASE_ID,
                endpoint_key=config.QNA_ENDPOINT_KEY,
                host=config.QNA_ENDPOINT_HOST
            )
        )

        self.user_state = user_state
        self.conv_state = conv_state
        self.language_preference_accessor = self.user_state.create_property(
            "LanguagePreference"
        )
    async def on_members_added_activity(
        self, members_added: [ChannelAccount], turn_context: TurnContext
    ):
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                await turn_context.send_activity(
                    """Greetings. Ask me a question. I will try to give an answer."""
                )

    async def on_message_activity(self, turn_context: TurnContext):
        qna_answered = False

        response = await self.qna_maker.get_answers(turn_context)
        if response and len(response) > 0:
            if response[0].score >= MAX_CONF_SCORE:
                qna_answered = True
                await turn_context.send_activity(response[0].answer)

        if not qna_answered:
            await turn_context.send_activity("No QnA Maker answers were found. " +
                                             "Connecting to knowledge base, just wait...")

            query = turn_context.activity.text.strip()
            response = self.get_answer(query)

            reply = MessageFactory.list([])

            if "dbpedia" in response.keys():
                abstract = []
                for entity in response["dbpedia"]:
                    abstract.append(response["dbpedia"][entity]["abstract"])
                    reply.attachments.append(
                        self.create_hero_card(response["dbpedia"][entity])
                    )

                if "wikidata" in response.keys():
                    reply.text = "Wikidata answer: " + [response["wikidata"][key]["property_id"]
                        for key in response["wikidata"]][0]
                else:
                    reply.text = "BERT model answer: " + self.make_prediction(abstract, query)
            else:
                reply.text = ("I can't answer this question. " +
                          "Please try to specify it as accurately as possible.")

            await turn_context.send_activity(reply)

    def create_hero_card(self, data) -> Attachment:
        abstract = translator.translate(data["abstract"], dest="ru").text
        if "thumbnail" in data.keys():
            image_url = data["thumbnail"]
        else:
            image_url = "https://commons.wikimedia.org/wiki/File:No_image_available.svg"
        card = HeroCard(
            text=abstract,
            title="Сущность, выделенная из вопроса",
            images=[
                CardImage(
                    url=image_url
                )
            ],
            buttons=[
                CardAction(
                    type=ActionTypes.open_url,
                    title="Перейти к ресурсу DBpedia",
                    value=data["entity"]
                )
            ]
        )
        return CardFactory.hero_card(card)
