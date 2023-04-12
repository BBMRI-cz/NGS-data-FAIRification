import shortuuid
import json
import sys
import os

def add_pseudo_ID(original_ID):
    if os.path.exists('pseudo_table.json'):
        with open('pseudo_table.json', 'r') as json_file:  #open file and load data to dictionary
            data = json.load(json_file)
    else:
        data = dict()                         #set up argv as original_ID
    if original_ID not in data.values():                  #find out if original_ID has no pseudonym so far
        pseudoID = "mmci_" + shortuuid.ShortUUID().random(length=24)
        with open('pseudo_table.json', 'w+') as outfile:         #write the data together with new original + pseudo ID
                data[pseudoID] = original_ID
                json.dump(data, outfile, indent=4)
        return pseudoID

if __name__ == "__main__":
    print(add_pseudo_ID(original_ID = sys.argv[1]))