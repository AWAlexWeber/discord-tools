import mysql.connector
import time
import os
import logging
import threading
import time
import requests
import json

from datetime import datetime
from Tools.tools import *
from dotenv import load_dotenv

class ChainPing():

    def __init__(self):
        self.chain = {}
        self.input_chain = {}
        self.chain_id = {}
        self.kill = False
        self.processed_kills = {}

        # Starting the process

    def get_chain(self):
        return self.chain

    # Stops the system
    def kill(self):
        self.kill = True

    def add_system(self, system):
        print_log("Chain Ping - Adding " + str(system))
        self.input_chain[system] = datetime.now()
        if system[0] == 'J' and system[1].isdigit() and system not in self.input_chain:
            self.input_chain[system] = datetime.now()

        self.chain_id[system] = self.get_solar_system_id(system)

    def remove_system(self, system):
        print_log("Chain Ping - Removing " + str(system))
        if system in self.input_chain:
            del self.input_chain[system]
            del self.chain_id[system]

    def process_chain(self):
        # Initial sleep
        print_log("Chain Ping - Sleeping")

        if num_system < int(os.getenv("MAP_MIN_SYSTEMS_TO_SLEEP")):
            time.sleep(int(os.getenv("MAP_SLEEP_MAX")))
        else:
            time.sleep(int(os.getenv("MAP_SLEEP_MIN")))

        # Processing the chain, then calling ourselves again 
        print_log("Chain Ping - Processing chain")

        if self.kill:
            return False

        # Duplicating the process chain into our system
        self.chain = self.input_chain.copy()

        num_system = 0
        for solar_system in self.chain:
            print_log("Chain Ping - Processing " + str(solar_system))
            num_system += 1

            datetime_string = self.chain[solar_system].strftime("%Y%m%d%H00")

            # Checking for any new kills
            zkill_request = requests.get('https://zkillboard.com/api/kills/systemID/'+str(self.chain_id[solar_system][0])+'/startTime/'+datetime_string+'/')
            
            zkill_response = json.loads(zkill_request.text)
            for kill in zkill_response:
                if kill['killmail_id'] in self.processed_kills:
                    continue

                self.processed_kills[kill['killmail_id']] = datetime.now()

                # Sending this out as a new notification...
                print_log("Chain Ping - Displaying " + str(kill))
            

            self.chain[solar_system] = datetime.now()
            time.sleep(int(os.getenv("MAP_SLEEP_MID")))

        # Sleeping a minimum value of time
        # Allows the process to sleep

        return True


    # Function that uses our local sql server to get the ID of a solar system from the name
    def get_solar_system_id(self, system):
        import mysql.connector

        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="arancar_is_dumb"
        )

        cursor = mydb.cursor()
        cursor.execute("SELECT db_static.mapsolarsystems.solarSystemID from db_static.mapsolarsystems WHERE solarSystemName = %s", (system,))

        return cursor.fetchall()[0]

    def process_map_update(self, message):
        message_embeds = message.embeds
        for embed in message_embeds:
            title_contents = embed.to_dict()['title']

            if 'Deleted system' in title_contents:
                system = title_contents[title_contents.find('\'') + 1:title_contents.rfind('\'')]
                self.remove_system(system)

            if 'Updated system ' in title_contents or 'Created system' in title_contents:
                system = title_contents[title_contents.find('\'') + 1:title_contents.rfind('\'')]
                self.add_system(system)
        