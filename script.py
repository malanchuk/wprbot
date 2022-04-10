import time
import numpy as np
import pyrogram
import asyncio
import logging
import os
import random
from colorama import init, Fore, Back, Style
import playsound

from threading import Thread

logging.basicConfig(level=logging.DEBUG)

app_id = 8
app_hash = '7245de8e747a0d6fbe11f7cc14fcc0bb'


def get_ses_list():
    ses_list = os.listdir('pyroses/')
    return ses_list


def link_to_info(link):
    full = link.split("/")
    # print(full)
    channel = full[3]
    post_id = int(full[4])
    return channel, post_id


async def mass(link, react, amount, sessions):
    channel, post_id = link_to_info(link)
    bad_list = []
    counter = 0
    for el in sessions:
        if counter >= amount:
            break

        try:
            app = pyrogram.Client(f"pyroses/{el.split('.')[0]}", api_id=app_id, api_hash=app_hash, proxy=dict(
                hostname="kproxy.site",
                port=12253,
                username="Et2eC6",
                password="AK2GuT8eV7GE"
            ))
            async with app:
                try:
                    # await app.join_chat(channel)
                    # await app.send_reaction(channel, post_id, react)
                    peer_ch = await app.resolve_peer(channel)
                    post2_id = [post_id]
                    await app.send(
                        pyrogram.raw.functions.messages.GetMessagesViews(peer=peer_ch, id=post2_id, increment=True))
                    counter += 1
                    print(f"{Fore.GREEN}[+] Ready {el}{Style.RESET_ALL} | Total Good: {counter}")

                except Exception as ex:
                    print(f"{Fore.RED}[-] Error {el} | {ex}{Style.RESET_ALL}")


        except Exception as ex:
            print(f"{Fore.RED}[-] Error {el} | {ex}{Style.RESET_ALL}")
            continue

        # await asyncio.sleep(1)


sessions = get_ses_list()

splited_ses = np.array_split(sessions, 5)

for sl in splited_ses:
    asyncio.get_event_loop().run_until_complete(mass("https://t.me/ruski_mir/382", "👍️️", 20, sl))

playsound.playsound('sound.wav', True)

# дизлайк=👎  лайк=👍   рыгаловка=🤮  heart=❤️  cry=😢 shit=💩
