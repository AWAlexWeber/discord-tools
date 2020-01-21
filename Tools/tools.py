# General import functionality
import os
import random
import discord
from dotenv import load_dotenv
from datetime import datetime

# Helper functions
def print_log(text):
    f = open(os.getenv("LOG_FILE"), 'a+')
    print(f'{datetime.now():%Y-%m-%d %H:%M:%S%z}' + " " + text, file=f)
    print(f'{datetime.now():%Y-%m-%d %H:%M:%S%z}' + " " + text)
    f.close()
    return

async def send_message(user, message, client):
    user = client.get_user(user)
    dm_channel = await user.create_dm()
    await dm_channel.send(message)

async def set_role_by_name(member, role_name):
    role_list = member.guild.roles
    for role in role_list:
        if str(role) == role_name:
            break

    await member.add_roles(role)

async def get_role_by_name(guild, role_name):
    role_list = guild.roles

    for role in role_list:
        if str(role) == role_name:
            break

    return role

def read_file_from_path(message_path):
    message_file = open(message_path, "r")
    message_list = message_file.readlines()
    message_file.close()

    message = ""
    for message_line in message_list:
        message += message_line

    return message
