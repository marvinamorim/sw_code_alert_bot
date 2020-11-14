from time import sleep


import dataset
import schedule
import requests

from config import settings
from telegram import send_code

db = dataset.connect(settings.DATABASE_URL)
table = db[settings.CODES]


def get_rewards(rewards):
    rewards_text = ""
    for reward in rewards:
        rewards_text += f'{reward["Quantity"]}x {reward["Sw_Resource"]["Label"]}\n'
    return rewards_text[:-1]


def find_nodes():
    r = requests.get(settings.URL_MAIN)
    codes = r.json()
    for code in codes["data"]:
        if code["Status"] == "verified" and table.find_one(code=code["Label"]) == None:
            rewards = get_rewards(code["Resources"])
            print("New Code: ", code["Label"])
            table.insert(dict(code=code["Label"]))
            send_code(code["Label"], rewards)


if __name__ == "__main__":
    find_nodes()
    schedule.every(5).minutes.do(find_nodes)
    while True:
        schedule.run_pending()
        sleep(1)
