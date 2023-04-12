import shortuuid
import json
import sys

with open('pseudo_table.json', 'r') as json_file:  #open file and load data to dictionary
    data = json.load(json_file)
original_ID = sys.argv[1]                           #set up argv as original_ID
if original_ID not in data.values():                  #find out if original_ID has no pseudonym so far
    pseudoID = "mmci_" + shortuuid.ShortUUID().random(length=12)
    while pseudoID in data.keys():               #checking if generated pseudo ID is uniq in our data
        pseudoID = "mmci_" + shortuuid.ShortUUID().random(length=12)
    with open('pseudo_table.json', 'w') as outfile:         #write the data together with new original + pseudo ID
            data[pseudoID] = original_ID
            json.dump(data, outfile, indent=6)









