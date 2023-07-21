import json
import os
import pandas as pd
import xml.etree.ElementTree as ET
import argparse
import uuid

class Pseudonymizer:
    """
    Pseudonymizer Class

    Attributes
    ----------
    run_path : str
        path to a sequencing run that will be pseudonymized and completed with clinical data
    export_path : str
        path to an file that consist of XML exports with biobank and clinical information
    pseudo_table_path :  str
        path to a pseudonymization json file

    Methods
    -------
    __call_(self)
        Performs the following steps:
            1. Pseudonymization of sample sheet
            2. Adding clinical and biobank data
            3. Pseudonymizing file names
    """

    xml_prefix = "{http://www.bbmri.cz/schemas/biobank/data}"

    def __init__(self, run_path, bbm_export_folder_path,
                 pseudonimisation_table_path, pseudonimisation_table_patient_path, pseudonimisation_table_samples_path):
        """
        Parameters
        ----------
        run_path : str
            path to a sequencing run that will be pseudonymized and completed with clinical data
        export_path : str
            path to an file that consist of XML exports with biobank and clinical information
        pseudo_table_path :  str
            path to a pseudonymization json file
        """

        self.run_path = run_path
        self.export_path = bbm_export_folder_path
        self.pseudo_table_path = pseudonimisation_table_path
        self.pseudo_patient_path = pseudonimisation_table_patient_path
        self.pseudo_samples_path = pseudonimisation_table_samples_path

    def __str__(self) -> str:
        return f"""Path to processed sequence run:\n {self.seq_path}\n
                Path to export folder:\n {self.export_path}\n
                Path to pseudonimisation_table: \n {self.pseudo_table_path}"""

    def __call__(self):
        self.pseudonymize_run()

    def pseudonymize_run(self):
        """Performs the following steps:
        1. Pseudonymization of sample sheet
        2. Adding clinical and biobank data
        3. Pseudonymizing file names
        """

        clinical_data, predictive_pseudo_tuples = self.pseudo_sample_sheet_and_get_clinical_data()
        self.save_clinical_data(clinical_data)
        predictive_pseudo_tuples.sort(key=lambda a: len(a[0]), reverse=True)
        self.create_temporary_pseudo_table(predictive_pseudo_tuples)
        self.locate_all_files_with_predictive_number(predictive_pseudo_tuples)

    def pseudo_sample_sheet_and_get_clinical_data(self):
        """Pseudonymizes run SampleSheet and 
        collect clinical data of predictive number in a given run

        Performs the following steps:
        1.Reads SampleSheet
        2.Pseudonymizes all predictive numbers
        3.Stores predictive:pseudo tuples to json
        4.Collects clinical data

        Returns
        -------
        clinical_data : List[Dict]
            List of dictionaries containing clinical information about a patient with a given predictive number
        predictive_pseudo_tuples : List[(str,str)]
            List of tuples (predictive_number:pseudonymized_number)
        """

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
        predictive_numbers = [predictive_number.replace("_", "-") for predictive_number in predictive_numbers]

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
        """Take single predictive number, create a shortuuid pseudonym
        Checks if pseudonymization json exists and of the predictive number was already pseudonymized

        Parameters
        ----------
        original_ID : str
            Predictive number that will be converted to pseudonymization number

        Returns
        -------
        pseudo_ID : str
            mmci_predictive_ + Randomly generated UUID of lenght 24
        """

        data = {"predictive":[]}
        if os.path.exists(self.pseudo_table_path):
            with open(self.pseudo_table_path, 'r') as json_file:
                data = json.load(json_file)
                pseudo_list = data["predictive"]
        else:
            pseudo_list = []                                 
        
        existing_ids = [val["predictive_number"] for val in pseudo_list]
        if original_ID not in existing_ids:                  
            pseudoID = "mmci_predictive_" + str(uuid.uuid4())
            with open(self.pseudo_table_path, 'w+') as outfile:
                sample = {
                    "predictive_number": original_ID,
                    "pseudo_number": pseudoID}

                pseudo_list.append(sample)
                data["predictive"] = pseudo_list
                json.dump(data, outfile, indent=4)
            return pseudoID
        else:
            for val in pseudo_list:
                if val["predictive_number"] == original_ID:
                    return val["pseudo_number"]

    def check_for_predictive_number_in_export(self, predictive_number, pseudo_number):
        """Looks if there are clinical data with a given predictive number

        Parameters
        ----------
        predictive_number : str
            Predictive number that will be converted to pseudonymization number

        pseudo_ID : str
            mmci_predictive + Randomly generated UUID of lenght 24

        Returns
        -------
        clinical_data : List[Dict]
            List of dictionaries containing clinical information about a patient with a given predictive number
        """

        clinical_data = []
        for export in os.listdir(self.export_path):
            export_path = os.path.join(self.export_path, export)
            tree = ET.parse(export_path)
            root = tree.getroot()
            lts = root.find(f"{self.xml_prefix}LTS")
            found_predictive = False
            sample_data = []
            for child in lts:
                if ("/" in child.attrib["predictive_number"] and
                self.fix_predictive_number(child.attrib["predictive_number"]) == predictive_number):
                    found_predictive = True
                    if "tissue" in child.tag:
                        sample_data.append(self.prepare_tissue(child, pseudo_number))
                    if "genome" in child.tag:
                        sample_data.append(self.prepare_genome(child, pseudo_number))
                    if "serum" in child.tag:
                        sample_data.append(self.prepare_serum(child, pseudo_number))

            if found_predictive:
                patient = {
                    "ID": self.generate_pseudo_patient_id(root.get("id")),
                    "Birth": f"{root.get('month')}/{root.get('year')}",
                    "Sex": root.get("sex"),
                    "Samples": sample_data
                }
                clinical_data.append(patient)

        return clinical_data

    def generate_pseudo_patient_id(self, original_ID):
        data = {"patients":[]}
        if os.path.exists(self.pseudo_patient_path):
            with open(self.pseudo_patient_path, 'r') as json_file:
                data = json.load(json_file)
                pseudo_list = data["patients"]
        else:
            pseudo_list = []

        existing_ids = [val["patient_ID"] for val in pseudo_list]
        if original_ID not in existing_ids:
            pseudoID = "mmci_patient_" + str(uuid.uuid4())
            with open(self.pseudo_patient_path, 'w+') as outfile:
                sample = {
                    "patient_ID": original_ID,
                    "patient_pseudo_ID": pseudoID}
                pseudo_list.append(sample)
                data["patients"] = pseudo_list
                json.dump(data, outfile, indent=4)
            return pseudoID
        else:
            for val in pseudo_list:
                if val["patient_ID"] == original_ID:
                    return val["patient_pseudo_ID"]

    def fix_predictive_number(self, predictive_number):
        """Unifies predictive number format
        Parameters
        ----------
        predictive_number : str
            Predictive number in an original format

        Returns
        -------
        predictive_formated : str
            Predictive number in adjusted format
        """

        part1 = predictive_number.split("/")[0][:2]
        part2 = predictive_number.split("/")[1]
        predictive_formated = f"{part2}-{part1}"
        return predictive_formated
    
    def prepare_tissue(self, lts_child, pseudo_number):
        """Unifies predictive number format
        Parameters
        ----------
        lts_child : xml.etree.ElementTree.Element
            XML element containing clinical information about the sequenced sample (Tissue)
        pseudo_number : str
            Pseudonymized predictive number that is added to the clinical information

        Returns
        -------
        info : Dict
            Dictionary containing clinical information about the sequenced sample (Tissue)
        """

        info = {
            "material": "tissue",
            "pseudoID": pseudo_number,
            "biopsyNumber": lts_child.get(f"biopsy"),
            "sampleID": self.generate_pseudo_sample_id(lts_child.get("sampleId")),
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
        """Unifies predictive number format
        Parameters
        ----------
        lts_child : xml.etree.ElementTree.Element
            XML element containing clinical information about the sequenced sample (Serum)
        pseudo_number : str
            Pseudonymized predictive number that is added to the clinical information

        Returns
        -------
        info : Dict
            Dictionary containing clinical information about the sequenced sample (Serum)
        """

        info = {
            "material": "serum",
            "pseudoID": pseudo_number,
            "biopsyNumber": lts_child.get(f"biopsy"),
            "sampleID": self.generate_pseudo_sample_id(lts_child.get("sampleId")),
            "sampleNumber": lts_child.find(f"{self.xml_prefix}samplesNo").text,
            "availableSamplesNumber": lts_child.find(f"{self.xml_prefix}availableSamplesNo").text,
            "materialType": lts_child.find(f"{self.xml_prefix}materialType").text,
            "diagnosis": lts_child.find(f"{self.xml_prefix}diagnosis").text,
            "takingDate": lts_child.find(f"{self.xml_prefix}takingDate").text
        }

        return info

    def prepare_genome(self, lts_child, pseudo_number):
        """Unifies predictive number format
        Parameters
        ----------
        lts_child : xml.etree.ElementTree.Element
            XML element containing clinical information about the sequenced sample (Genome)
        pseudo_number : str
            Pseudonymized predictive number that is added to the clinical information

        Returns
        -------
        info : Dict
            Dictionary containing clinical information about the sequenced sample (Genome)
        """

        info = {
            "material": "genome",
            "pseudoID": pseudo_number,
            "biopsyNumber": lts_child.get(f"biopsy"),
            "sampleID": self.generate_pseudo_sample_id(lts_child.get("sampleId")),
            "sampleNumber": lts_child.find(f"{self.xml_prefix}samplesNo").text,
            "availableSamplesNumber": lts_child.find(f"{self.xml_prefix}availableSamplesNo").text,
            "materialType": lts_child.find(f"{self.xml_prefix}materialType").text,
            "takingDate": lts_child.find(f"{self.xml_prefix}takingDate").text
        }

        return info

    def generate_pseudo_sample_id(self, original_sample_id):
        data = {"samples":[]}
        if os.path.exists(self.pseudo_samples_path):
            with open(self.pseudo_samples_path, 'r') as json_file:
                data = json.load(json_file)
                pseudo_list = data["samples"]
        else:
            pseudo_list = []

        existing_ids = [val["sample_ID"] for val in pseudo_list]
        if original_sample_id not in existing_ids:
            pseudoID = "mmci_sample_" + str(uuid.uuid4())
            with open(self.pseudo_samples_path, 'w+') as outfile:
                sample = {
                    "sample_ID": original_sample_id,
                    "pseudo_sample_ID": pseudoID}
                pseudo_list.append(sample)
                data["samples"] = pseudo_list
                json.dump(data, outfile, indent=4)
            return pseudoID
        else:
            for val in pseudo_list:
                if val["sample_ID"] == original_sample_id:
                    return val["pseudo_sample_ID"]
    
    def save_clinical_data(self, clinical_data_list):
        """Save clinical data to json file 'clinical_info.json'

        Parameters
        ----------
        clinical_data_list : List[Dict]
            List of dictionaries containing clinical information about a patient with a given predictive number
        """

        clinical_data_list = self.remove_duplcate_dicts(clinical_data_list)
        clinical_data_dict = {"clinical_data": clinical_data_list}
        with open(os.path.join(self.run_path, "clinical_info.json"), "w") as f:
            json.dump(clinical_data_dict, f, indent=4)

    def remove_duplcate_dicts(self, dict_list):
        """Remove duplicates from List[Dict]
        
        Parameters
        ----------
        dict_list : List[Dict]
            List of dictionaries containing duplicates
        
        Returns
        -------
        dict_list_unique : List[Dict]
            List of dictionaries without duplicates
        """
        old_list = [tuple(d.items()) for d in dict_list]
        start=0
        no_duplicates = self.remove_duplicate(start, old_list, [])
        dict_no_duplicates = [dict(t) for t in list(no_duplicates)]

        return dict_no_duplicates

    def remove_duplicate(self, start, oldlist, newlist):
        if start==len(oldlist):return newlist  #base condition
        if oldlist[start] not in newlist:   #checking whether element present in new list  or not
            newlist.append(oldlist[start])

        return self.remove_duplicate(start+1, oldlist, newlist)


    def create_temporary_pseudo_table(self, predictive_pseudo_tuples):
        """Create a temporary pseudonymisation_table json file consisting
        only of predictive:pseudo tuples of a current run

        Parameters
        ----------
        predictive_pseudo_tuples : List[(str:str)]
            List of predictive:pseudo tuples
        """

        pseudo_list = [{"predictive_number": pred, "pseudo_number": pseudo} for pred, pseudo in predictive_pseudo_tuples] 
        data = {"pseudonimisation": pseudo_list}
        with open(f"{self.pseudo_table_path}.temp", 'w+') as outfile:
            json.dump(data, outfile, indent=4)

    def locate_all_files_with_predictive_number(self, predictive_pseudo_tuples):
        """Locate all files in a run that contain a predictive number in the name 
        and replace it with pseudonymized predictive number

        Parameters
        ----------
        predictive_pseudo_tuples : List[(str:str)]
            List of predictive:pseudo tuples
        """

        for pred, pseudo in predictive_pseudo_tuples:
            self.rename_files_recursively(pred, pseudo, self.run_path)

    def rename_files_recursively(self, text_to_replace, replaced_text, current_file):
        """Recursively renames all files ina run that contain predictive number with
        pseudonymized predictive number. Does it in a way to not create conflicts in a renaming

        Parameters
        ----------
        text_to_replace : str
            Text that should be replaced in a file name
        replaced_text : str
            Text that will replace "text_to_replace" in a file name
        current_file : str
            Path of a current directory that will be renamed and then listed to rename inner file
        """
        
        current_file_renamed = current_file[::-1].replace(text_to_replace[::-1], replaced_text[::-1], 1)[::-1]
        os.rename(current_file, current_file_renamed)
        for file in os.listdir(current_file_renamed):
            file_path = os.path.join(current_file_renamed, file)
            if os.path.isdir(file_path):
                self.rename_files_recursively(text_to_replace, replaced_text, file_path)
            else:
                os.rename(os.path.join(current_file_renamed, file), os.path.join(current_file_renamed, file.replace(text_to_replace, replaced_text)))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Pseudonymizer",
        description="Pseudonymize sequencing run and adds clinical data to it")
    parser.add_argument("-r", "--run", type=str, required=True, help="Path to sequencing run path that will be pseudonymized")
    parser.add_argument("-e", "--export", type=str, required=True, help="Path to Biobank Export to extract clinical data")
    parser.add_argument("-d", "--pred_pseudo", type=str, required=True, help="Path to predictive pseudonymization json file")
    parser.add_argument("-p", "--patients_pseudo", type=str, required=True, help="Path to patient pseudonymization json file")
    parser.add_argument("-s", "--samples_pseudo", type=str, required=True, help="Path to samples pseudonymization json file")
    args = parser.parse_args()
    
    run_path = Pseudonymizer(args.run, args.export, args.pred_pseudo, args.patients_pseudo, args.samples_pseudo)()
    print(run_path)