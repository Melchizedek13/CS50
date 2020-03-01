from config import *
import logger
from telethon import TelegramClient, connection, events


logger = logger.get_logger()

bot = TelegramClient('bot', API_ID, API_HASH,
                     connection=connection.ConnectionTcpMTProxyRandomizedIntermediate,
                     proxy=(MTPROXY_URL, MTPROXY_PORT, MTPROXY_SECRET)
                     ).start(bot_token=BOT_TOKEN)


@bot.on(events.NewMessage(pattern='/start'))
async def send_welcome(event):
    await event.reply('Howdy, how are you doing?')

if __name__ == '__main__':
    bot.run_until_disconnected()
