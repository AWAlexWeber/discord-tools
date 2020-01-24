# File for performing API checks
# importing the requests library
import requests
import time
import json

# MySQL connector
import mysql.connector

<<<<<<< HEAD
from datetime import datetime

=======
>>>>>>> 5547fd9ac7d25622a8cde568f2d2814b64a6895c
# Statics
TARGET_YEAR = 2019
ZKILL_API_SLEEP_TIME = 1
ESI_API_SLEEP_TIME = 2

STATIC_MONTH_LIST = [1,2,3,4,5,6,7,8,9,10,11,12]
START_POINT = "J171818"

wspace_file_path = "/home/vsmanagementbot/StatisticGen/wspaceList"
regionclass_file_path = "/home/vsmanagementbot/StatisticGen/regionClass"
system_output_file = "/home/vsmanagementbot/StatisticGen/kill_output"
system_format_output = "/home/vsmanagementbot/StatisticGen/kill_output_format"

kill_full_output = "/home/vsmanagementbot/StatisticGen/kill_output_format_full"

# Building mysql connector
def get_connector():
    mydb = mysql.connector.connect(
<<<<<<< HEAD
        host="localhost",
        user="root",
        passwd="arancar_is_dumb"
=======
        host=,
        user=,
        passwd=
>>>>>>> 5547fd9ac7d25622a8cde568f2d2814b64a6895c
    )
    return mydb

# Getting the region ID
def get_region_from_name(solarSystemName):
    mydb = get_connector()
    cursor = mydb.cursor()

    try:
        cursor.execute("SELECT regionID from db_static.mapsolarsystems WHERE solarSystemName = %s",(solarSystemName,))
        result = cursor.fetchall()
        return result[0][0]

    except:
        print("An error has occured")
        exit()


# Generating the hash table containing the regions mapped to class
def gen_region_dictionary(file_path):

    # Opening the file
    region_file = open(file_path)

    region_dictionary = {}

    line = region_file.readline()
    while line:
        region_id = line[:line.index(",")]
        class_id = line[line.index(",")+1:-1]

        region_dictionary[region_id] = class_id

        line = region_file.readline()

    return region_dictionary


# Building the container for our w-space
# Function for generating the SystemContainer table
def gen_system_container(file_path, region_dictionary):

    # Opening the file
    wspace_list_file = open(file_path)

    # Getting the region
    system_list = list()

    line = wspace_list_file.readline()
    while line:
        solarSystemName = str(line[0:7])
        solarSystemID = line[9:17]
        regionID = line[19:-1]
        className = region_dictionary[regionID]

        # Building the system class
        tmp_system_container = SystemContainer(solarSystemID, solarSystemName, className, regionID)
        system_list.append(tmp_system_container)

        # Next line
        line = wspace_list_file.readline()

    return system_list

# Function that makes the API call
def fetch_zkill_url(URL):
    request = requests.get(url = URL)
    data = request.json()
    time.sleep(ZKILL_API_SLEEP_TIME)
    return data

# Function that makes the API call
def fetch_esi_url(URL):
    request = requests.get(url = URL)
    if (request.status_code != 200):
        
        print(URL)
        print("SERIOUS FAILURE HAS OCCURED")
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        print(dt_string)	

        return None

    data = request.json()
    time.sleep(ESI_API_SLEEP_TIME)
    return data


# Iteratively performing pulls
def pull_wspace_data(system_container):

    # Initializing the URL
    target_url = "https://zkillboard.com/api/kills/solarSystemID/"

    # Now we perform getting the zkill hashes and kill ID
    found_start = False

    for system in system_container:

        if not found_start and not START_POINT == None and not system.solarSystemName == START_POINT:
            print("Skipping " + system.solarSystemName)
            continue
        if system.solarSystemName == START_POINT:
            found_start = True

        target_month = 1

        while target_month <= 12:

            target_page = 1
            result_size = 50000

            while result_size >= 200:
                full_url = target_url + system.solarSystemID + "/year/" + str(TARGET_YEAR) + "/month/" + str(target_month) + "/page/" + str(target_page) + "/"
                results = fetch_zkill_url(full_url)

                result_size = len(results)
                
                print("Processing " + str(system.solarSystemName) + " with month of " + str(target_month))

                for result in results:
                    system.month_table[target_month].append(result)

                target_page = target_page + 1

            target_month = target_month + 1

        save_system_output(system)

# Writting the system to the output file
def save_system_output(system):
    print("Saving out " + str(system.solarSystemName))
    kill_output = open(system_output_file,"a")
    kill_output.write(json.dumps(system.__dict__))
    kill_output.close()

class SystemContainer:

    def __init__(self,_solarSystemID, _solarSystemName, _solarSystemClass, _regionID):
        self.solarSystemID = _solarSystemID
        self.solarSystemName = _solarSystemName
        self.solarSystemClass = _solarSystemClass
        self.regionID = _regionID
        self.init_months()

    def init_months(self):
        self.month_table = {}
        for month in STATIC_MONTH_LIST:
            self.month_table[month] = list()

    def toString(self):
        return(self.solarSystemName+","+self.solarSystemID+","+self.solarSystemClass+","+self.regionID)

def gen_format_output(system_container):

    format_output = open(system_format_output,"w")

    system_index = 0
    character_count = 0
    num_systems = len(system_container)
    with open(system_output_file) as kill_output:
        
        current_system = system_container[system_index]
        current_system_name = current_system.solarSystemName

        # Continually processing
        cur_string = str()
        while True:
            cur_char = kill_output.read(1)
            if not cur_char:
                print("End of file")
                break
            cur_string += cur_char
            character_count += 1
            if len(cur_string) % 20000 == 0:
                print("Character: " + str(len(cur_string)))
            
            if cur_string.__contains__(current_system_name):

                # Saving output
                cur_char = kill_output.read(2)
                cur_string+=cur_char
                format_output.write(cur_string)
                format_output.write("\n")
                percent_complete = float(system_index) / float(num_systems)
                percent_complete_output = str(current_system_name) + " - " + str(100*round(percent_complete,4)) + "%"
                print('{0}\r'.format(percent_complete_output))

                # Modifying our current system
                system_index+=1
                current_system = system_container[system_index]
                current_system_name = current_system.solarSystemName

                cur_string = str()

            if not cur_char:
                break

        format_output.close()
        kill_output.close()

    print("Total characters: " + str(character_count))

def process_output_format(region_dictionary):
    mydb = get_connector()
    cursor = mydb.cursor()

    format_output_file = open(system_format_output)

    line = format_output_file.readline()
    count = 0
    num_systems = 2604

    total_value = 0
    num_kills = 0

    class_dictionary = {}
    class_dictionary["C1"] = {"kills": 0, "isk": 0}
    class_dictionary["C2"] = {"kills": 0, "isk": 0}
    class_dictionary["C3"] = {"kills": 0, "isk": 0}
    class_dictionary["C4"] = {"kills": 0, "isk": 0}
    class_dictionary["C5"] = {"kills": 0, "isk": 0}
    class_dictionary["C6"] = {"kills": 0, "isk": 0}
    class_dictionary["C13"] = {"kills": 0, "isk": 0}

    month_dictionary = {}

    while line:
        json_data = json.loads(line)
        line = format_output_file.readline()
        
        json_data["solarSystemClass"] = region_dictionary[json_data['regionID']]

        for month in json_data['month_table']:
            for kill in json_data['month_table'][month]:
                '''
                if kill['zkb']['totalValue'] <= 100000:
                    continue
                if kill['zkb']['awox'] == True:
                    continue
                if kill['zkb']['solo'] == True:
                    continue
                if kill['zkb']['npc'] == True:
                    continue
                '''

                total_value += kill['zkb']['totalValue']
                num_kills += 1

                if not month in month_dictionary:
                    month_dictionary[month] = {"kills": 0, "isk": 0,

                        "class": {
                            "C1": {"kills": 0, "isk": 0},
                            "C2": {"kills": 0, "isk": 0},
                            "C3": {"kills": 0, "isk": 0},
                            "C4": {"kills": 0, "isk": 0},
                            "C5": {"kills": 0, "isk": 0},
                            "C6": {"kills": 0, "isk": 0},
                            "C13": {"kills": 0, "isk": 0}
                        }
                    }

                month_dictionary[month]['kills']=month_dictionary[month]['kills']+1
                month_dictionary[month]['isk']=month_dictionary[month]['isk']+kill['zkb']['totalValue']

                month_dictionary[month]["class"][json_data["solarSystemClass"]]['kills']=month_dictionary[month]["class"][json_data["solarSystemClass"]]['kills']+1
                month_dictionary[month]["class"][json_data["solarSystemClass"]]['isk']=month_dictionary[month]["class"][json_data["solarSystemClass"]]['isk']+kill['zkb']['totalValue']

                class_dictionary[json_data["solarSystemClass"]]["kills"]+=1
                class_dictionary[json_data["solarSystemClass"]]["isk"]+=kill['zkb']['totalValue']

                kill_id = kill['killmail_id']
                npc = kill['zkb']['npc']
                points = kill['zkb']['points']
                awox = kill['zkb']['awox']
                total_value = kill['zkb']['totalValue']
                fitted_value = kill['zkb']['fittedValue']
                month = month
                kill_hash = kill['zkb']['hash']
                location_id = kill['zkb']['locationID']
                system = json_data['solarSystemName']
                system_class = region_dictionary[json_data['regionID']]

                mysql_insert = "INSERT INTO db_stats.tb_kills_raw (kill_id, kill_hash, npc, points, total_value, fitted_value, awox, location_id, system, month, system_class) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                data_array = (kill_id, kill_hash, npc, points, total_value, fitted_value, awox, location_id, system, month, system_class)
                cursor.execute(mysql_insert,data_array)
                mydb.commit()

        # Printing progress
        percent_complete = float(count) / float(num_systems)
        percent_complete_output = str(100*round(percent_complete,4)) + "%"
        print('{0}\r'.format(percent_complete_output))
        count = count + 1


    '''
    for key in class_dictionary:
        #isk_to_kill_ration = round(class_dictionary[key]['isk'] / class_dictionary[key]['kills'] / 1000000)
        #print(str(isk_to_kill_ration) + key)

    for key in class_dictionary:
        #class_dictionary[key]["isk"] = str(round(class_dictionary[key]["isk"]/1000000000)) + " billion"

    print(class_dictionary)
    for key in sorted (month_dictionary.keys()):  
        month_dictionary[key]["isk"] = str(round(month_dictionary[key]["isk"]/1000000000)) + ""

        for class_type in month_dictionary[key]["class"]:
            month_dictionary[key]["class"][class_type]["isk"] = str(round(month_dictionary[key]["class"][class_type]["isk"]/1000000000)) + ""

    
    print(month_dictionary)

    print("Month\tISK(B)\tKills C1 ISK\tC2 ISK\tC3 ISK\tC4 ISK\tC5 ISK\tC6 ISK\tC13 Kills\tC1 Kills\tC2 Kills\tC3 Kills\tC4 Kills\tC5 Kills\tC6 Kills\tC13 Kills")
    for key in sorted (month_dictionary.keys()):
        
        print(key+"\t"+str(month_dictionary[key]["isk"])+"\t"+str(month_dictionary[key]["kills"]), end=" ")
        for class_type in sorted (month_dictionary[key]["class"].keys()):
            if class_type == "C13":
                continue
            print(month_dictionary[key]["class"][class_type]['isk'],end='\t')
        print(month_dictionary[key]["class"]["C13"]['isk'],end='\t')
        print("\t", end="")
        for class_type in sorted (month_dictionary[key]["class"].keys()):
            if class_type == "C13":
                continue
            print(str(month_dictionary[key]["class"][class_type]['kills']),end='\t\t')
        print(str(month_dictionary[key]["class"]["C13"]['kills']),end='\t')
        print("")'''

def pull_from_ccp_esi():

    # Initializing the URL
    target_url = "https://esi.evetech.net/latest/killmails/"

    # Pulling data from our local mysql database
    mydb = get_connector()
    cursor = mydb.cursor()

    print("Starting request all...")
    pull_all_data = "SELECT * FROM db_stats.tb_kills_raw"
    cursor.execute(pull_all_data)
    results = cursor.fetchall()
    print("Finished request all!")

    kill_output = open(kill_full_output, "a")

    count = 0
    target_value = 60616
    num_kills = len(results) 
    for kill in results:

        while count < target_value:
            count+=1
            continue

        if count == target_value:
            print("Finished skip")
            percent_complete = float(count) / float(num_kills)
            percent_complete_output = str(100*round(percent_complete,4)) + "%" + " ("+ str(count) + " of " + str(num_kills) + ")"
            print('{0}\r'.format(percent_complete_output))
            now = datetime.now()
            dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
            print(dt_string)	
            time.sleep(0.01)

        count+=1

        full_url = target_url + str(kill[0])
        full_url = full_url + "/"
        full_url = full_url + str(kill[1])
        full_url = full_url + "/?datasource=tranquility"
        
        kill_full = None
        while kill_full == None:
            kill_full = fetch_esi_url(full_url)

        kill_output.write(str(kill_full))
        kill_output.write("\n")

        # Printing progress
        if (count % 1000) == 0:
            percent_complete = float(count) / float(num_kills)
            percent_complete_output = str(100*round(percent_complete,4)) + "%" + " ("+ str(count) + " of " + str(num_kills) + ")"
            print('{0}\r'.format(percent_complete_output))
            now = datetime.now()
            dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
            print(dt_string)	

            time.sleep(0.01)
        

    
def process_esi_output():

    count = 0
    num_kills = len(results) 
    for kill in results:

        full_url = target_url + str(kill[0])
        full_url = full_url + "/"
        full_url = full_url + str(kill[1])
        full_url = full_url + "/?datasource=tranquility"
        
        kill_full = None
        while kill_full == None:
            kill_full = fetch_esi_url(full_url)

        # Processing the kill
        # First, performing the update to our tb_kills_full table
        update_sql = "UPDATE db_stats.tb_kills_full SET killmail_time = %s, total_damage = %s WHERE kill_id = %s"
        cursor.execute(update_sql, (kill_full["killmail_time"], kill_full["victim"]["damage_taken"], kill[0]))
        mydb.commit()
        break

        # Printing progress
        if (count % 100) == 0:
            percent_complete = float(count) / float(num_kills)
            percent_complete_output = str(100*round(percent_complete,4)) + "%" + " ("+ str(count) + " of " + str(num_kills) + ")"
            print('{0}\r'.format(percent_complete_output))
            now = datetime.now()
            dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
            print(dt_string)	
            time.sleep(0.01)

        count = count + 1

def get_full_length():
    kill_output = open(kill_full_output, "r")

    count = 0
    for line in kill_output.readlines():
        count = count + 1

    print(count)


# Main
# Generating container

# Main processing
region_dictionary = gen_region_dictionary(regionclass_file_path)
#system_container = gen_system_container(wspace_file_path, region_dictionary)
#pull_wspace_data(system_container)

# Minor processing of output file
#gen_format_output(system_container)

# Going through all kills
#process_output_format(region_dictionary)

# Requesting CCP's ESI for information
#get_full_length()
pull_from_ccp_esi()
