import mysql.connector
import time
import os
import logging
import threading
import time
import requests
import json
import random
import discord
import asyncio

import datetime as dt
from datetime import datetime, timedelta

from Tools.tools import *
from dotenv import load_dotenv

class ChainPing():

    def __init__(self):
        # Some discord management stuff
        self.client = None
        self.client_channel = None

        # Assigning some chain ping stuff
        self.kill = False
        self.num_system = 0
        self.processed_kills = {}
        self.chain = {}

        load_dotenv()

        # Starting the process

    def initialize_discord_client(self, client):
        print_log("Chain Ping - Initializing Discord Client")
        self.client = client

        # All we need to do is grab the channel we are going to be sending the chain ping messages to
        for guild in self.client.guilds:
            if str(guild.id) == os.getenv("CHAIN_PING_OUTPUT_DISCORD_ID"):
                for channel in guild.text_channels:
                    if str(channel.id) == os.getenv("CHAIN_PING_OUTPUT_CHANNEL_ID"):
                        self.client_channel = channel
                        break

    def get_chain(self):
        return self.chain

    # Stops the system
    def kill(self):
        self.kill = True

    def get_pathfinder_chain(self):
        mydb = mysql.connector.connect(
            host=os.getenv("MYSQL_SERVER_PATHFINDER_HOST"),
            user=os.getenv("MYSQL_SERVER_PATHFINDER_USERNAME"),
            passwd=os.getenv("MYSQL_SERVER_PATHFINDER_PASSWORD")
        )

        cursor = mydb.cursor()

        SELECT_ACTIVE_SYSTEM = "SELECT active, mapId, systemId, alias FROM pathfinder.system WHERE active = 1 AND mapId = 5"
        cursor.execute(SELECT_ACTIVE_SYSTEM)
        chain = cursor.fetchall()

        cursor.close()
        mydb.close()

        return chain

    def get_esi_kill(self, hash, id):

        # Grabbing the ESI information
        url = 'https://esi.evetech.net/latest/killmails/'+str(id)+'/'+str(hash)+'/?datasource=tranquility'
        esi_kill = requests.get(url)

        if esi_kill.status_code != 200:
            return -1

        return json.loads(esi_kill.text)

    def get_player_info(self, player_id):

        # Grabbing the ESI information
        url = 'https://esi.evetech.net/latest/characters/'+str(player_id)+'/?datasource=tranquility'
        esi_player = requests.get(url)

        if esi_player.status_code != 200:
            return -1

        return json.loads(esi_player.text)

    def get_ship_info(self, ship_id):

        mydb = mysql.connector.connect(
            host=os.getenv("localhost"),
            user=os.getenv("MYSQL_SERVER_USERNAME"),
            passwd=os.getenv("MYSQL_SERVER_PASSWORD")
        )

        cursor = mydb.cursor()

        GET_SHIP_INFO = "SELECT * FROM db_static.invtypes WHERE typeID = %s "
        cursor.execute(GET_SHIP_INFO, (ship_id,))
        result = cursor.fetchall()
        ship_name = result

        cursor.close()
        mydb.close()

        return ship_name

    def get_solar_system_info(self, solar_system_id):

        mydb = mysql.connector.connect(
            host=os.getenv("localhost"),
            user=os.getenv("MYSQL_SERVER_USERNAME"),
            passwd=os.getenv("MYSQL_SERVER_PASSWORD")
        )

        cursor = mydb.cursor()

        GET_SOLAR_SYSTEM_NAME = "SELECT solarSystemID, solarSystemName FROM db_static.mapsolarsystems WHERE solarSystemID = %s "
        cursor.execute(GET_SOLAR_SYSTEM_NAME, (solar_system_id,))
        result = cursor.fetchall()
        solar_system_info = result

        cursor.close()
        mydb.close()

        return solar_system_info

    def get_corp_info(self, corp_id):

        # Grabbing the ESI information
        url = 'https://esi.evetech.net/latest/corporations/'+str(corp_id)+'/?datasource=tranquility'
        esi_corp = requests.get(url)

        if esi_corp.status_code != 200:
            return -1

        return json.loads(esi_corp.text)

    def process_chain(self, loop):
        # Initial sleep
        time.sleep(10)

        # Sleeping a minimum value of time to not spam zkill with requests

        print_log("Chain Ping - Sleeping")

        if self.num_system > int(os.getenv("MAP_MIN_SYSTEMS_TO_SLEEP")):
            print("Chain Ping - Sleeping for " + os.getenv("MAP_SLEEP_MAX"))
            time.sleep(int(os.getenv("MAP_SLEEP_MAX")))
        else:
            print("Chain Ping - Sleeping for " + os.getenv("MAP_SLEEP_MAX"))
            time.sleep(int(os.getenv("MAP_SLEEP_MIN")))

        # Processing the chain, then calling ourselves again 
        print_log("Chain Ping - Processing chain")

        if self.kill:
            return False

        datetime_start = dt.time(10,30,0)
        datetime_end = dt.time(12,0,0)
        datetime_now = datetime.now().time()
        datetime_now = dt.time(hour=datetime_now.hour, minute=datetime_now.minute, second=0)

        if time_in_range(datetime_start, datetime_end, datetime_now):
            time.sleep(int(os.getenv("MAP_SLEEP_MIN")))
            return True

        # Duplicating the process chain into our system
        pathfinder_chain = self.get_pathfinder_chain()
        self.num_system = len(pathfinder_chain)
        
        for solar_system in pathfinder_chain:
            solar_system_id = solar_system[2]
            solar_system_alias = solar_system[3]

            if solar_system_id in self.chain:
                datetime_string = self.chain[solar_system_id].strftime("%Y%m%d%H00")
                print_log("Request chain for " + str(solar_system_id) + " to " + str(datetime_string))
            else:
                datetime_string = (datetime.now() - timedelta(hours=0, minutes=60)).strftime("%Y%m%d%H00")
                print_log("Updating chain (now) for " + str(solar_system_id) + " to " + str(datetime_string))

            # Checking for any new kills
            url = 'https://zkillboard.com/api/kills/systemID/'+str(solar_system_id)+'/startTime/'+datetime_string+'/'
            #print_log("Chain Ping - Processing " + str(solar_system[3]) + " with url of " + str(url))
            zkill_request = requests.get(url)

            print(zkill_request)
            
            zkill_response = json.loads(zkill_request.text)

            # Building list of everything to display
            kill_display_list = []

            for kill in zkill_response:
                if kill['killmail_id'] in self.processed_kills:
                    continue

                # Constructing a list of all the kills to display that happened in this system
                kill_display_list.append(kill)

            for kill in kill_display_list:
                kill_esi = self.get_esi_kill(kill['zkb']['hash'],kill['killmail_id'])

                if kill_esi == -1:
                    print_log("Chain Ping - Error, failed to load kill esi")
                    return True

                kill_url = url = 'https://zkillboard.com/kill/' + str(kill['killmail_id'])

                victim = self.get_player_info(kill_esi['victim']['character_id'])

                if victim == -1:
                    print_log("Chain Ping - Error, failed to load victim esi")
                    return True

                victim_corporation = self.get_corp_info(kill_esi['victim']['corporation_id'])

                if victim_corporation == -1:
                    print_log("Chain Ping - Error, failed to load victim corporation")
                    return True

                ship_json = self.get_ship_info(kill_esi['victim']['ship_type_id'])

                victim_name = victim['name']
                corporation_name = victim_corporation['name']
                corporation_ticker = victim_corporation['ticker']
                ship_name = ship_json[0][2]

                # Going through the attackers
                final_blow_attacker = None
                attacker_count = len(kill_esi['attackers'])
                for attacker in kill_esi['attackers']:
                    if attacker['final_blow'] == True:
                        final_blow_attacker = attacker
                        break

                attacker_character_id = final_blow_attacker['character_id']
                attacker_corporation_id = final_blow_attacker['corporation_id']
                attacker_ship = final_blow_attacker['ship_type_id']

                attacker = self.get_player_info(attacker_character_id)['name']

                if attacker == -1:
                    print_log("Chain Ping - Error, failed to load attacker esi")
                    return True

                attacker_corporation = self.get_corp_info(attacker_corporation_id)['name']

                if attacker_corporation == -1:
                    print_log("Chain Ping - Error, failed to load attacker corporation")
                    return True
                attacker_ship_name = self.get_ship_info(attacker_ship)
                print(attacker_ship_name)
                attacker_ship_name = attacker_ship_name[0][2]

                attacker_name_em = "["+attacker+"](""https://zkillboard.com/character/" + str(attacker_character_id) +")"
                attacker_corporation_em = "["+attacker_corporation+"](https://zkillboard.com/corporation/"+str(attacker_corporation_id)+")"

                victim_name_em = "["+victim_name+"](""https://zkillboard.com/character/" + str(kill_esi['victim']['character_id']) +")"
                victim_corporation_em = "["+corporation_name+"](https://zkillboard.com/corporation/"+str(kill_esi['victim']['corporation_id'])+")"

                solar_system_name = self.get_solar_system_info(solar_system_id)[0][1]
                solar_system_name_em = "["+solar_system_name+"](https://zkillboard.com/system/" + str(solar_system_id) +")"

                loss_value = int(kill['zkb']['totalValue'])
                display_loss_value = loss_value
                if loss_value / 1000 >= 1:
                    display_loss_value = str(round(loss_value / 1000, 2)) + "k ISK"
                if loss_value / 1000000 >= 1:
                    display_loss_value = str(round(loss_value / 1000000,2)) + "m ISK"
                if loss_value / 1000000000 >= 1:
                    display_loss_value = str(round(loss_value / 1000000000,2)) + "b ISK"
                

                loss_time = kill_esi['killmail_time']
                loss_date_time = " On " + loss_time[5:7] + "/" + loss_time[8:10] + " at " + loss_time[11:16]

                embeded = discord.Embed(
                    image="https://images.evetech.net/types/"+str(kill_esi['victim']['ship_type_id'])+"/icon",
                    title='Kill: ' + ship_name + ' destroyed in ' + solar_system_name + " ("+solar_system_alias+")", 
                    color=3066993,
                    url=kill_url, 
                    description="**"+victim_name_em + "** (**"+victim_corporation_em+"**) lost their **" + ship_name + "** in **" + solar_system_name_em + "** to **" + attacker_name_em + "** (**" + attacker_corporation_em + "**) in a **" + attacker_ship_name + "** and **" + str(attacker_count) + "** others"
                )

                avatar_url = "https://cdn.discordapp.com/avatars/" + str(self.client.user.id) + "/" + str(self.client.user.avatar) + ".png"
                embeded.set_author(name=self.client.user.name, icon_url=avatar_url)
                embeded.set_thumbnail(url="https://images.evetech.net/types/"+str(kill_esi['victim']['ship_type_id'])+"/icon" )
                embeded.set_footer(text="Value: " + display_loss_value + " | " + loss_date_time)

                loop.create_task(send_channel_message_embed(self.client_channel, embeded))

                # Sleeping while processing just to keep esi pinging low
                self.processed_kills[kill['killmail_id']] = datetime.now()
                time.sleep(1)

            self.chain[solar_system_id] = datetime.now() - timedelta(hours=0, minutes=60)
            #print_log("Updating chain for " + str(solar_system_id) + " to " + str(self.chain[solar_system_id]))
            time.sleep(int(os.getenv("MAP_SLEEP_MID")))

        # Processing the timestamps on our already processed kills and removing the ones that are too old
        delete_list = []
        for kill in self.processed_kills:
            if (datetime.now() - self.processed_kills[kill]).seconds / 60 > 90:
                print("Deleting " + str(kill))
                delete_list.append(kill)

        for kill in delete_list:
            del self.processed_kills[kill]

        return True

def time_in_range(start, end, x):
    """Return true if x is in the range [start, end]"""
    if start <= end:
        return start < x < end
    else:
        return start <= x or x <= end