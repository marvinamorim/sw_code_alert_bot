import dataset
import telebot

from config import settings

db = dataset.connect(settings.DATABASE_URL)
table = db[settings.USER]
bot = telebot.TeleBot(settings.TOKEN)


@bot.message_handler(commands=["start"])
def start(message):
    if table.find_one(id=message.chat.id) == None:
        response = (
            "Welcome to the Summoners War Code Alert.\n"
            "You are now subscribed to be alerted when a new code is registered at: "
            "https://swq.jp/l/en-US/\n"
            "To unsubscribe, send the message: /exit"
        )
        user_name = message.from_user.username
        full_name = (
            f"{message.from_user.first_name}" f"{message.from_user.last_name.strip()}"
            if message.from_user.last_name != None
            else ""
        )
        print("New user", user_name, full_name)
        table.insert(dict(id=message.chat.id, user_name=user_name, full_name=full_name))
    else:
        response = "You are already subscribed."
    bot.send_message(message.chat.id, response)


@bot.message_handler(commands=["exit"])
def start(message):
    if table.find_one(id=message.chat.id) == None:
        response = (
            "You are not subscribed.\n"
            "Send the message /start to subscribe to new Summoners War Promotion Codes"
        )
    else:
        response = (
            "You are now unsubscribed.\n"
            "If you want to subscribe again, send the message: /start"
        )
        table.delete(id=message.chat.id)
    print(f"User {message.chat.id} left")
    bot.send_message(message.chat.id, response)


def send_code(code, rewards):
    response = (
        f"New code available\nReward(s): {rewards}\n"
        f"{code}\n"
        f"http://withhive.me/313/{code}"
    )
    users = table.find()
    for user in users:
        bot.send_message(user["id"], response)
    return True


def send_error(id, error):
    print(error)
    bot.send_message(id, f"There was an error processing your request.")


if __name__ == "__main__":
    bot.polling()
