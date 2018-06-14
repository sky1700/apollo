from discord.ext import commands
from sqlalchemy.orm import joinedload

from event_bot.models import Event, EventChannel, Guild
from event_bot.queries import find_or_create_guild


class EventCommand:
    MAX_CAPACITY = 40
    MAX_DESC_LENGTH = 250
    MAX_TITLE_LENGTH = 100

    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    @commands.guild_only()
    async def event(self, ctx):
        """Create a new event"""
        await ctx.send("Event creation instructions have been messaged to you.")
        event = await self._get_event_from_user(ctx)
        with self.bot.transaction.new() as session:
            session.add(event)
        await ctx.author.send("Your event has been created!")


    async def _get_capacity_from_user(self, ctx):
        """Retrieve the event capacity from the user"""
        await ctx.author.send("Enter the maximum number of attendees (type 'None' for no limit):")
        while True:
            resp = (await self.bot.get_next_pm(ctx.author)).content
            if resp.upper() == 'NONE':
                return None
            elif resp.isdigit() and int(resp) in range(1, self.MAX_CAPACITY):
                return int(resp)
            else:
                await ctx.author.send(f"Entry must be between 1 and {self.MAX_CAPACITY} (or 'None' for no limit). Try again:")


    async def _get_desc_from_user(self, ctx):
        """Retrieve the event description from the user"""
        await ctx.author.send("Enter event description (type 'None' for no description):")
        while True:
            resp = (await self.bot.get_next_pm(ctx.author, timeout=240)).content
            if resp.upper() == 'NONE':
                return None
            elif len(resp) <= self.MAX_DESC_LENGTH:
                return resp
            else:
                await ctx.author.send(f"Event description must be less than {self.MAX_DESC_LENGTH} characters. Try again:")


    async def _get_event_channel(self, ctx):
        """Find or create the event channel for the current guild"""
        guild = find_or_create_guild(self.bot.transaction, ctx.guild.id, joinedload('event_channels'))
        if guild.has_multiple_event_channels():
            return guild.event_channels[0]
        else:
            channel = await self.bot.create_discord_event_channel(ctx.guild)
            return EventChannel(id=channel.id, guild_id=ctx.guild.id)


    async def _get_title_from_user(self, ctx):
        """Retrieve the event title from the user"""
        await ctx.author.send("Enter the event title:")
        while True:
            title = (await self.bot.get_next_pm(ctx.author)).content
            if len(title) <= self.MAX_TITLE_LENGTH:
                return title
            else:
                await ctx.author.send(f"Event title must be less than {self.MAX_TITLE_LENGTH} characters. Try again:")


    async def _get_event_from_user(self, ctx):
        """Create an event with user input via private messages"""
        event = Event()
        event.title = await self._get_title_from_user(ctx)
        event.description = await self._get_desc_from_user(ctx)
        event.capacity = await self._get_capacity_from_user(ctx)
        event.event_channel = await self._get_event_channel(ctx)
        return event