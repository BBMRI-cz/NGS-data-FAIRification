import shortuuid
import json
import os
import pandas as pd

def add_pseudo_ID(original_ID):
    if os.path.exists('pseudo_table.json'):
        with open('pseudo_table.json', 'r') as json_file:  #open file and load data to dictionary
            data = json.load(json_file)
    else:
        data = dict()                         #set up argv as original_ID
    if original_ID not in data.values():                  #find out if original_ID has no pseudonym so far
        pseudoID = "mmci_" + shortuuid.ShortUUID().random(length=24)
        with open('pseudo_table.json', 'w+') as outfile:         #write the data together with new original + pseudo ID
                data[original_ID] = pseudoID
                json.dump(data, outfile, indent=4)
        return pseudoID

def pseudo_sample_sheet(path_to_sample_sheet):
    df = pd.read_csv(path_to_sample_sheet, delimiter=";")
    sample_list_header = df["[Header]"].to_list()
    sample_list_second = df["Unnamed: 1"].to_list()
    id = sample_list_header.index("Sample_ID") +1

    pseudo_list = [add_pseudo_ID(val) for val in sample_list_header[id:]]

    new_column_header = sample_list_header[:id] + pseudo_list
    new_column_second = sample_list_second[:id] + pseudo_list

    df.drop(["[Header]", "Unnamed: 1"], axis=1, inplace=True)
    df.insert(loc=0, column="", value = new_column_second)
    df.insert(loc=0, column="[Header]",  value = new_column_header)
    df.columns = ["[Header]"] + ["" for i in range(len(df.columns) - 1)]
    df.fillna('', inplace=True)
    df.to_csv(path_to_sample_sheet, index=False)

def pseudo_fastQ(path_to_BaseCalls):
    with open('pseudo_table.json', 'r') as json_file:  #open file and load data to dictionary
        data = json.load(json_file)
    path = "../data/201230_M02340_0245_000000000-JDJ7Y/Data/Intensities/BaseCalls"
    for file in os.listdir(path):
        if file.endswith("fastq.gz") and not file.startswith("Undetermined"):
            name_split  = file.split("_")
            name_split[0] = data[name_split[0]]
            new_name = "_".join(name_split)
            print(os.path.join(path, file))
            print(os.path.join(path, new_name))
            #os.rename(os.path.join(path, file), os.path.join(path, new_name))



if __name__ == "__main__":
    pseudo_sample_sheet("../data/SampleSheet.csv")
    pseudo_fastQ("../data/201230_M02340_0245_000000000-JDJ7Y/Data/Intensities/BaseCalls")
