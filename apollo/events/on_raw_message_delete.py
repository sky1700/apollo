from apollo.queries import find_event_from_message
from apollo.services import ListEvents


class OnRawMessageDelete:

    def __init__(self, bot):
        self.bot = bot


    async def on_raw_message_delete(self, payload):
        if not self.bot.cache.event_exists(payload.message_id): return

        # If the message is marked for deletion, it was deleted by the bot
        # as part of clearing the event channel. Unmark it, and return.
        if self.bot.cache.message_marked_for_deletion(payload.message_id):
            return self.bot.cache.unmark_message_for_deletion(
                payload.message_id
                )

        session = self.bot.Session()

        event = find_event_from_message(session, payload.message_id)
        session.delete(event)
        self.bot.cache.delete_event(event.message_id)
        await ListEvents(self.bot, event.event_channel).call()

        session.commit()
        session.close()
