import logging

from discord import Message
from discord.ext.commands import Bot, Cog

from config import CONFIG


class Publish(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @Cog.listener()
    async def on_message(self, message: Message):
        if (
            message.channel.id not in CONFIG.AUTO_PUBLISH_CHANNELS
            or not message.channel.is_news()
        ):
            return
        logging.info(f"Publishing message with id {message.id} in {message.channel}")
        await message.publish()

    async def cog_command_error(self, ctx, error):
        logging.exception(error)


def setup(bot: Bot):
    bot.add_cog(Publish(bot))
