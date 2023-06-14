import shortuuid
import json
import os
import pandas as pd
import xml.etree.ElementTree as ET
import argparse

class Pseudonymizer:

    xml_prefix = "{http://www.bbmri.cz/schemas/biobank/data}"
    
    def __init__(self, run_path, bbm_export_folder_path, pseudonimisation_table_path):
        self.run_path = run_path
        self.export_path = bbm_export_folder_path
        self.pseudo_table_path = pseudonimisation_table_path

    def __str__(self) -> str:
        return f"""Path to processed sequence run:\n {self.seq_path}\n
                Path to export folder:\n {self.export_path}\n
                Path to pseudonimisation_table: \n {self.pseudo_table_path}"""

    def __call__(self):
        self.pseudonymize_run()

    def pseudonymize_run(self):
        clinical_data, predictive_pseudo_tuples = self.pseudo_sample_sheet()
        self.save_clinical_files(clinical_data)
        predictive_pseudo_tuples.sort(key=lambda a: len(a[0]), reverse=True)
        self.create_temporary_pseudo_table(predictive_pseudo_tuples)
        self.locate_all_files_with_predictive_number(predictive_pseudo_tuples)

    def pseudo_sample_sheet(self):
        sample_sheet_path = os.path.join(self.run_path, "SampleSheet.csv")
        df = pd.read_csv(sample_sheet_path, delimiter=",",
                 names=["[Header]","Unnamed: 1","Unnamed: 2","Unnamed: 3","Unnamed: 4",
                 "Unnamed: 5","Unnamed: 6","Unnamed: 7","Unnamed: 8","Unnamed: 9"])
        
        sample_list_header = df["[Header]"].to_list()
        sample_list_second = df["Unnamed: 1"].to_list()
        id = sample_list_header.index("Sample_ID") +1

        pseudo_list = []
        clincal_data = []

        predictive_numbers = sample_list_header[id:]

        for pred_number in predictive_numbers:
            pseudo_id = self.add_pseudo_ID(pred_number)
            clincal_data += self.check_for_predictive_number_in_export(pred_number, pseudo_id)
            pseudo_list.append(pseudo_id)

        new_column_header = sample_list_header[:id] + pseudo_list
        new_column_second = sample_list_second[:id] + pseudo_list

        df.drop(["[Header]", "Unnamed: 1"], axis=1, inplace=True)
        df.insert(loc=0, column="", value = new_column_second)
        df.insert(loc=0, column="[Header]",  value = new_column_header)
        df.columns = ["[Header]"] + ["" for i in range(len(df.columns) - 1)]
        df.fillna('', inplace=True)
        df.to_csv(sample_sheet_path, header=False, index=False)

        predictive_pseudo_tuples = [(predictive_numbers[i], pseudo_list[i]) for i in range(len(predictive_numbers))]

        return clincal_data, predictive_pseudo_tuples

    def add_pseudo_ID(self, original_ID):
        data = {"pseudonimisation":[]}
        if os.path.exists(self.pseudo_table_path):
            with open(self.pseudo_table_path, 'r') as json_file:
                data = json.load(json_file)
                pseudo_list = data["pseudonimisation"]
        else:
            pseudo_list = []                                 
        
        existing_ids = [val["predictive_number"] for val in pseudo_list]
        if original_ID not in existing_ids:                  
            pseudoID = "mmci_" + shortuuid.ShortUUID().random(length=24)
            with open(self.pseudo_table_path, 'w+') as outfile:
                sample = {
                    "predictive_number": original_ID,
                    "pseudo_number": pseudoID}

                pseudo_list.append(sample)
                data["pseudonimisation"] = pseudo_list
                json.dump(data, outfile, indent=4)
            return pseudoID
        else:
            for val in pseudo_list:
                if val["predictive_number"] == original_ID:
                    return val["pseudo_number"]

    def check_for_predictive_number_in_export(self, predictive_number, pseudo_number):
        clinicalData = []
        for export in os.listdir(self.export_path):
            export_path = os.path.join(self.export_path, export)
            tree = ET.parse(export_path)
            root = tree.getroot()
            lts = root.find(f"{self.xml_prefix}LTS")
            for child in lts:
                if ("/" in child.attrib["predictive_number"] and
                self.fix_predictive_number(child.attrib["predictive_number"]) == predictive_number):
                    if "tissue" in child.tag:
                        clinicalData.append(self.prepare_tissue(child, pseudo_number))
                    if "genome" in child.tag:
                        clinicalData.append(self.prepare_genome(child, pseudo_number))
                    if "serum" in child.tag:
                        clinicalData.append(self.prepare_serum(child, pseudo_number))
        
        return clinicalData
    
    def fix_predictive_number(self, predictive_number):
        part1 = predictive_number.split("/")[0][:2]
        part2 = predictive_number.split("/")[1]
        return f"{part2}-{part1}"
    
    def prepare_tissue(self, lts_child, pseudo_number):
        info = {
            "material": "tissue",
            "pseudoID": pseudo_number,
            "biopsyNumber": lts_child.get(f"biopsy"),
            "sampleID": lts_child.get("sampleId"),
            "sampleNumber": lts_child.find(f"{self.xml_prefix}samplesNo").text,
            "availableSamplesNumber": lts_child.find(f"{self.xml_prefix}availableSamplesNo").text,
            "materialType": lts_child.find(f"{self.xml_prefix}materialType").text,
            "pTNM": lts_child.find(f"{self.xml_prefix}pTNM").text,
            "morphology": lts_child.find(f"{self.xml_prefix}morphology").text,
            "diagnosis": lts_child.find(f"{self.xml_prefix}diagnosis").text,
            "cutTime": lts_child.find(f"{self.xml_prefix}cutTime").text,
            "freezeTime": lts_child.find(f"{self.xml_prefix}freezeTime").text,
            "retrieved": lts_child.find(f"{self.xml_prefix}retrieved").text,
            }
        return info

    def prepare_serum(self, lts_child, pseudo_number):
        info = {
            "material": "serum",
            "pseudoID": pseudo_number,
            "biopsyNumber": lts_child.get(f"biopsy"),
            "sampleID": lts_child.get("sampleId"),
            "sampleNumber": lts_child.find(f"{self.xml_prefix}samplesNo").text,
            "availableSamplesNumber": lts_child.find(f"{self.xml_prefix}availableSamplesNo").text,
            "materialType": lts_child.find(f"{self.xml_prefix}materialType").text,
            "takingDate": lts_child.find(f"{self.xml_prefix}takingDate").text
        }

        return info

    def prepare_genome(self, lts_child, pseudo_number):
        info = {
            "material": "genome",
            "pseudoID": pseudo_number,
            "biopsyNumber": lts_child.get(f"biopsy"),
            "sampleID": lts_child.get("sampleId"),
            "sampleNumber": lts_child.find(f"{self.xml_prefix}samplesNo").text,
            "availableSamplesNumber": lts_child.find(f"{self.xml_prefix}availableSamplesNo").text,
            "materialType": lts_child.find(f"{self.xml_prefix}materialType").text,
            "takingDate": lts_child.find(f"{self.xml_prefix}takingDate").text
        }

        return info
    
    def save_clinical_files(self, clinical_data_list):
        clinical_data_list = self.remove_duplcate_dicts(clinical_data_list)
        clinical_data_dict = {"clinical_data": clinical_data_list}
        with open(os.path.join(self.run_path, "clinical_info.json"), "w") as f:
            json.dump(clinical_data_dict, f, indent=4)

    def remove_duplcate_dicts(self, dict_list):
        return [dict(t) for t in {tuple(d.items()) for d in dict_list}]

    def create_temporary_pseudo_table(self, predictive_pseudo_tuples):
        pseudo_list = [{"predictive_number": pred, "pseudo_number": pseudo} for pred, pseudo in predictive_pseudo_tuples] 
        data = {"pseudonimisation": pseudo_list}
        with open(f"{self.pseudo_table_path}.temp", 'w+') as outfile:
            json.dump(data, outfile, indent=4)

    def locate_all_files_with_predictive_number(self, predictive_pseudo_tuples):
        for pred, pseudo in predictive_pseudo_tuples:
            self.rename_files_recursively(pred, pseudo, self.run_path)

    def rename_files_recursively(self, text_to_replace, replaced_text, current_file):
        current_file_renamed = current_file[::-1].replace(text_to_replace[::-1], replaced_text[::-1], 1)[::-1]
        os.rename(current_file, current_file_renamed)
        for file in os.listdir(current_file_renamed):
            file_path = os.path.join(current_file_renamed, file)
            if os.path.isdir(file_path):
                self.rename_files_recursively(text_to_replace, replaced_text, file_path)
            else:
                os.rename(os.path.join(current_file_renamed, file), os.path.join(current_file_renamed, file.replace(text_to_replace, replaced_text)))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pseudonymize sequencing run and adds clinical data to it")
    parser.add_argument("-r", "--run", type=str, required=True)
    parser.add_argument("-e", "--export", type=str, required=True)
    parser.add_argument("-p", "--pseudo", type=str, required=True)
    
    args = parser.parse_args()
    
    Pseudonymizer(args.run, args.export, args.pseudo)()