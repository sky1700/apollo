from .embeds import event_embed
from . import emojis as emoji


async def list_events(bot, event_channel):
    """Clear the event channel and populate it with events"""
    channel = bot.get_channel(event_channel.id)
    await channel.purge()

    for event in event_channel.events:
        embed = event_embed(channel.guild, event)
        event_msg = await channel.send(embed=embed)
        await _add_rsvp_reactions(event_msg)
        event.message_id = event_msg.id

    bot.db.add(event_channel)


async def update_event(bot, event):
    """Update an event message in place"""
    channel = bot.get_channel(event.event_channel.id)
    event_message = await channel.get_message(event.message_id)
    embed = event_embed(channel.guild, event)
    await event_message.edit(embed=embed)


async def _add_rsvp_reactions(msg):
    """Add reaction 'rsvp buttons' to a message"""
    await msg.add_reaction(emoji.CHECK)
    await msg.add_reaction(emoji.CROSS)
    await msg.add_reaction(emoji.QUESTION)
