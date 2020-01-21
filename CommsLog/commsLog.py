# General import functionality
import os
import random
import discord
import datetime
from Tools.tools import *
from dotenv import load_dotenv
from datetime import datetime

async def log_channel_change(member, before, after):

    # Grabbing a list of all the voice channels to monitor
    channel_log_message = None

    if before.channel == None and after.channel != None:
        channel_log_message = "["+str(member)+"][JOINED]["+str(after.channel)+"]"
    elif after.channel == None and before.channel != None:
        channel_log_message = "["+str(member)+"][LEFT]["+str(before.channel)+"]"
    elif before.channel != None and after.channel != None and str(before.channel) != str(after.channel):
        channel_log_message = "["+str(member)+"][MOVED][FROM]["+str(before.channel)+"][TO]["+str(after.channel)+"]"

    for text_channel in member.guild.channels:
        if str(text_channel) == os.getenv("COMMS_LOG_TO_NAME"):
            break

    if channel_log_message == None:
        print_log("An error has occured " + str(member) + " | | | " + str(before) + " | | | " + str(after))
    else:
        current_time = datetime.now()
        channel_log_message = "[" + str(current_time.strftime("%Y-%m-%d %H:%M:%S")) + "]" + channel_log_message
        print_log(channel_log_message)
        await text_channel.send(channel_log_message)
