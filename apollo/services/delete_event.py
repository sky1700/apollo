from apollo.list_events import ListEvents


class DeleteEvent:

    def __init__(self, bot, session, event, member):
        self.bot = bot
        self.session = session
        self.event = event
        self.member = member


    async def call(self):
        if self._member_can_delete():
            self.session.delete(self.event)
            await ListEvents(self.bot, self.event.event_channel).call()
        else:
            await self.member.send("You don't have permission to do that.")


    def _channel(self):
        return self.bot.get_channel(self.event.event_channel.id)


    def _member_can_delete(self):
        return self._member_has_manage_guild() or self._member_owns_event()


    def _member_has_manage_guild(self):
        return self.member.permissions_in(self._channel()).manage_guild


    def _member_owns_event(self):
        return self.event.organizer.id == self.member.id
