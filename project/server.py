from config import *
import logger
from telethon import TelegramClient, connection, events


logger = logger.get_logger()

# Initialize bot
bot = TelegramClient('bot', TG_API_ID, TG_API_HASH,
                     connection=connection.ConnectionTcpMTProxyRandomizedIntermediate,
                     proxy=(MTPROXY_URL, MTPROXY_PORT, MTPROXY_SECRET)
                     ).start(bot_token=TG_BOT_TOKEN)


@bot.on(events.NewMessage(pattern='/start'))
async def send_welcome(event):
    await event.reply('Howdy, how are you doing?')


@bot.on(events.NewMessage)
async def echo_all(event):
    me = await event.get_user()
    print(me.username)
    await event.reply(event.text)


if __name__ == '__main__':
    bot.run_until_disconnected()
