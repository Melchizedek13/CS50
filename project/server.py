from telethon import TelegramClient, connection, events

import logger
import os
from config import *

logger = logger.get_logger()

# Initialize bot
bot = TelegramClient(os.path.join('db', DB_NAME), TG_API_ID, TG_API_HASH,
                     connection=connection.ConnectionTcpMTProxyRandomizedIntermediate,
                     proxy=(MTPROXY_URL, MTPROXY_PORT, MTPROXY_SECRET)
                     ).start(bot_token=TG_BOT_TOKEN)

# print(bot.session.filename)


@bot.on(events.NewMessage(pattern='/start'))
async def send_welcome(event):
    sender = await event.get_sender()
    logger.info(sender)

    await event.respond(f'Hi, {sender.first_name}!')
    raise events.StopPropagation


@bot.on(events.NewMessage)
async def echo_all(event):
    await event.reply('**I do not know such a command!**')


def main():
    """Start the bot."""
    bot.run_until_disconnected()


if __name__ == '__main__':
    main()
