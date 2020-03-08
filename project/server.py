from telethon import TelegramClient, connection, events

import logger
from categories import Categories, check_categories_exist
from config import *
import expenses
import exceptions

logger = logger.get_logger()

# Initialize bot
bot = TelegramClient(os.path.join('db', DB_NAME), TG_API_ID, TG_API_HASH,
                     connection=connection.ConnectionTcpMTProxyRandomizedIntermediate,
                     proxy=(MTPROXY_URL, MTPROXY_PORT, MTPROXY_SECRET)
                     ).start(bot_token=TG_BOT_TOKEN)

# print(bot.session.filename)
check_categories_exist()


@bot.on(events.NewMessage(pattern='(/start|/help)'))
async def send_welcome(event):
    sender = await event.get_sender()
    logger.debug(sender)

    await event.respond(
        f"Hi, {sender.first_name}!\n"
        "It's a bot for accounting expenses.\n"
        "Daily stats: /today\n"
        "Monthly stats: /month\n"
        "Categories: /categories"
    )
    raise events.StopPropagation


@bot.on(events.NewMessage(pattern='/categories'))
async def categories_list(event):
    """Sending category expenses list"""
    categories = Categories().get_all_categories()
    respond_message = "Expenses category:\n\n+ " + \
                      ("\n+ ".join([c.name + ' (' + ", ".join(c.aliases) + ')' for c in categories]))
    await event.respond(respond_message)
    raise events.StopPropagation


@bot.on(events.NewMessage(pattern='/today'))
async def today_statistics(event):
    respond_message = expenses.get_today_statistics()
    await event.respond(respond_message)
    raise events.StopPropagation


@bot.on(events.NewMessage(pattern='/month'))
async def today_statistics(event):
    respond_message = expenses.get_month_statistics()
    await event.respond(respond_message)
    raise events.StopPropagation


@bot.on(events.NewMessage)
async def add_expense(event):
    try:
        expense = expenses.add_expense(event.message.message)
    except exceptions.NotCorrectMessage as e:
        await event.respond(str(e))
        return

    respond_message = (
        f"The expense {expense.amount} rub was added on {expense.category_name}.\n\n"
        f"{expenses.get_today_statistics()}"
    )
    await event.respond(respond_message)


def main():
    """Start the bot."""
    bot.run_until_disconnected()


if __name__ == '__main__':
    main()
