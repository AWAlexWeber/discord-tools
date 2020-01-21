# General import functionality
import os
import random
import discord
import signal
import asyncio
import sys

from SecretSanta.secretSanta import *
from CommsLog.commsLog import *
from Tools.tools import *
from Welcome.welcome import *
from ChainPing.chainPing import *
from dotenv import load_dotenv
from datetime import datetime

# <<<---------- Signal Handling ---------->>> #
def signal_handler(signal, frame):
    print_log("Process Terminated Manually")
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

# <<<---------- Signal Complt ---------->>> #

# <<<---------- Client Set-Up ---------->>> #
def load_chain_ping(client, chain_ping):
    ### Handling the discord bot posting the chain
    @client.event
    async def on_message(message):

        discord_map = os.getenv("MAP_DISC_ID")
        if str(message.channel.id) == discord_map:
            chain_ping.process_map_update(message)

    return client

def load_client():

    ### Initializing client; will run with token in main
    client = discord.Client()

    @client.event
    async def on_ready():
        print_log("Viper Sovereign Management - Online ")

    ### Handling the welcome message for the VS Recruitment Discord
    @client.event
    async def on_member_join(member):
        print_log("New member has joined managed server: ")
        print_log(str(member) + " has joined " + str(member.guild) + " " + str(member.guild.id))

        if str(member.guild.id) == os.getenv("GUILD_RECRUITMENT_ID"):
            await handle_welcome_recruit(member, client)

    ### Handling the voice logging tool for the VS Main Discord
    @client.event
    async def on_voice_state_update(member, before, after):
        
        if str(member.guild.id) == os.getenv("COMMS_LOG_GUILD_ID"):
            print_log("Logging member joining or disconnecting from VS Comms")
            await log_channel_change(member, before, after)

    return client
# <<<---------- Completed Set-Up ---------->>> #

# <<<---------- Initialization.. ---------->>> #

### Loading the environmental variables
load_dotenv()
time.sleep(1)

### Loading our client variables
token = os.getenv("DISCORD_TOKEN")
chain_ping = ChainPing()
client = load_client()
client = load_chain_ping(client, chain_ping)

async def start_client():
    await client.start(token)

def start_client_loop(loop):
    loop.run_forever()

def start_chain_ping():
    print_log("Chain Ping - Online")
    time.sleep(5)
    while (chain_ping.process_chain()):
        chain_ping.process_chain()

def init():
    asyncio.get_child_watcher()
    loop = asyncio.get_event_loop()
    loop.create_task(start_client())

    thread_client = threading.Thread(target=start_client_loop, args=(loop,))
    thread_client.start()

    thread_chain = threading.Thread(target=start_chain_ping, args=())
    thread_chain.start()

init()

# <<<---------- Completed Initialization ---------->>> #