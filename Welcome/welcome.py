# General import functionality
import os
import random
import discord
from Tools.tools import *
from dotenv import load_dotenv
from datetime import datetime

async def handle_welcome_recruit(member, client):
    # Determining which member has joined
    print_log("Welcoming member")

    # Getting roles and determining which one matches what we are looking for
    await set_role_by_name(member, os.getenv("RECRUITMENT_JOIN_ROLE"))

    # Messaging the member
    message = read_file_from_path(os.getenv("RECRUITMENT_JOIN_MESSAGE_PATH")).replace("$USER", str(member))
    message = message[0:message.find("#")] + message[message.find("#") + 5:]
    await send_message(member.id, message, client)

    # Notifying leadership in the main channel
    text_channel_list = member.guild.text_channels
    for text_channel in text_channel_list:
        if str(text_channel) == os.getenv("RECRUITMENT_NOTIFY_CHANNEL"):
            break

    notify_role_1 = os.getenv("RECRUITMENT_NOTIFY_ROLE_1")
    notify_role_id_1 = await get_role_by_name(member.guild, notify_role_1)
    notify_role_id_1 = str(notify_role_id_1.id)

    notify_role_2 = os.getenv("RECRUITMENT_NOTIFY_ROLE_2")
    notify_role_id_2 = await get_role_by_name(member.guild, notify_role_2)
    notify_role_id_2 = str(notify_role_id_2.id)

    member_id = str(member.id)

    await text_channel.send("<@"+member_id+"> has joined as a new recruit <@&"+notify_role_id_1+"> " + "<@&"+notify_role_id_2+">")

    