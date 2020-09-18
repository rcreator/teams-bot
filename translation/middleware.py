from typing import Callable, Awaitable, List

from botbuilder.core import Middleware, UserState, TurnContext
from botbuilder.schema import Activity, ActivityTypes

from translation import TranslatorM
from translation.settings import TranslatorSettings


class TranslatorMiddleware(Middleware):
    def __init__(self, translator: TranslatorM, user_state: UserState):
        self.translator = translator
        self.language_preference_accessor = user_state.create_property(
            "LanguagePreference"
        )

    async def on_turn(
        self, turn_context: TurnContext, logic: Callable[[TurnContext], Awaitable]
    ):
        if turn_context.activity.type == ActivityTypes.message:
            turn_context.activity.text = await self.translator.translate(
                turn_context.activity.text, TranslatorSettings.bot_language.value
            )

        async def aux_on_send(
            turn_context: TurnContext, activities: List[Activity], next_send: Callable
        ):
            user_language = await self.language_preference_accessor.get(
                turn_context, TranslatorSettings.user_language.value
            )

            for activity in activities:
                await self._translate_message_activity(activity, user_language)

            return await next_send()

        async def aux_on_update(
            turn_context: TurnContext, activity: Activity, next_update: Callable
        ):
            user_language = await self.language_preference_accessor.get(
                turn_context, TranslatorSettings.user_language.value
            )

            if activity.type == ActivityTypes.message:
                await self._translate_message_activity(activity, user_language)

            return await next_update()

        turn_context.on_send_activities(aux_on_send)
        turn_context.on_update_activity(aux_on_update)

        await logic()

    async def _translate_message_activity(self, activity: Activity, lang: str):
        if activity.type == ActivityTypes.message:
            activity.text = await self.translator.translate(
                activity.text, lang
            )
