# General import functionality
import os
import random
import discord
from Tools.tools import *
from dotenv import load_dotenv
from datetime import datetime

async def secret_santa(client):
    # Loading the secret santa information
    user_name_list = os.getenv('SECRET_SANTA_LIST').split(",")
    user_id_list = os.getenv('SECRET_SANTA_ID_LIST').split(",")

    # Randomizing the selection
    copy_list = user_name_list[:]
    pair_table = {}
    user_id_table = {}

    # Randomly generating pairs
    for index in range(0,len(user_name_list)):
        user_id_table[user_name_list[index]] = user_id_list[index]
        random_index = index
        while random_index == index or copy_list[random_index] == "":
            random_index = random.randrange(0, len(user_name_list))

        # Getting user names
        start_user = user_name_list[index]
        pair_user = user_name_list[random_index]

        pair_table[start_user] = pair_user

        # Getting the copy list set
        copy_list[random_index] = ""

    output_vlist_sender = [0] * len(user_name_list)
    input_vlist_sender = [0] * len(user_name_list)

    # Generating our safety hash
    index = 0
    for key in pair_table:
        #print(key + "\t\t\t" + pair_table[key])
        output_vlist_sender[index] = int(user_id_table[key])
        input_vlist_sender[index] = int(user_id_table[pair_table[key]])
        index = index + 1

    # Shuffling the lists
    random.shuffle(output_vlist_sender)
    random.shuffle(input_vlist_sender)

    # Finalziing and sending messages
    message_block = os.getenv("SECRET_SANTA_MESSAGE")
    for key in pair_table:
        send_block = message_block
        send_block = send_block.replace("$USER", key)
        send_block = send_block.replace("$TARGET", pair_table[key])
        await send_message(int(user_id_table[key]),send_block,client)

    print("Pairing complete!")
    print("Verification is as follows")
    for index in range(0,len(output_vlist_sender)):
        print(output_vlist_sender[index],input_vlist_sender[index])