SELECT db_static.invtypes.raceID, db_static.invtypes.groupID, db_static.invtypes.typeName, db_static.invgroups.groupName 
FROM db_static.invtypes INNER JOIN db_static.invgroups WHERE
db_static.invtypes.groupID = db_static.invgroups.groupID AND (
db_static.invtypes.groupID = 29 OR # Pods 
db_static.invtypes.groupID = 237 OR # Corvettes
db_static.invtypes.groupID = 31 OR # Shuttles
db_static.invtypes.groupID = 25 OR # Frigates
db_static.invtypes.groupID = 324 OR # Assault
db_static.invtypes.groupID = 830 OR # Covert Ops
db_static.invtypes.groupID = 893 OR # Electronic Attack
db_static.invtypes.groupID = 831 OR # Interceptors
db_static.invtypes.groupID = 1527 OR # Logistic
db_static.invtypes.groupID = 1283 OR # Expedition
db_static.invtypes.groupID = 420 OR # Destroyers
db_static.invtypes.groupID = 1534 OR # Command 
db_static.invtypes.groupID = 541 OR # Interdictors
db_static.invtypes.groupID = 1305 OR # Tactical
db_static.invtypes.groupID = 26 OR # Cruisers
db_static.invtypes.groupID = 1972 OR # Flag
db_static.invtypes.groupID = 832 OR # Logi
db_static.invtypes.groupID = 894 OR # HIC
db_static.invtypes.groupID = 358 OR # Heavy Assault
db_static.invtypes.groupID = 833 OR # Force Recon
db_static.invtypes.groupID = 906 OR # Combat Recon
db_static.invtypes.groupID = 963 OR # Strategic
db_static.invtypes.groupID = 28 OR # Industrial haulers
db_static.invtypes.groupID = 419 OR # Combat
db_static.invtypes.groupID = 1201 OR # Attack
db_static.invtypes.groupID = 540 OR # Command
db_static.invtypes.groupID = 27 OR # Battleships
db_static.invtypes.groupID = 898 OR # Black Ops
db_static.invtypes.groupID = 900 OR # Marauders
db_static.invtypes.groupID = 547 OR # Carrier
db_static.invtypes.groupID = 485 OR # Dreadnaught
db_static.invtypes.groupID = 1538 OR # FAX
db_static.invtypes.groupID = 659 OR # Super Carrier
db_static.invtypes.groupID = 30 # Titans
);
