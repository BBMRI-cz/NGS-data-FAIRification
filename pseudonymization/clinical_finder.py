import json
import uuid
import os
import xml.etree.ElementTree as ET
import copy

class Material:

    xml_prefix = "{http://www.bbmri.cz/schemas/biobank/data}"

    def __init__(self, lts_child, pseudo_number, sample_table):
        self.pseudo_id = pseudo_number
        self.biopsy_number = lts_child.get(f"biopsy")
        self.sample_ID = self._generate_pseudo_sample_id(lts_child.get("sampleId"), sample_table)
        self.sample_number = lts_child.find(f"{self.xml_prefix}samplesNo").text
        self.available_samples_number = lts_child.find(f"{self.xml_prefix}availableSamplesNo").text
        self.material_type = lts_child.find(f"{self.xml_prefix}materialType").text

    def __eq__(self, other) -> bool:
        if isinstance(other, Material):
            return self.sample_ID == other.sample_ID
        return False

    def __hash__(self) -> int:
        return hash(("sample_id", self.sample_ID))

    def __lt__(self, other) -> bool:
        if isinstance(self, Tissue) and isinstance(other, Tissue):
            return int(self.material_type) < int(other.material_type)
        elif isinstance(self, Tissue) and (isinstance(other, Serum) or isinstance(other, Genome)):
            return True
        elif isinstance(self, Serum) and (isinstance(other, Tissue)):
            return False
        elif isinstance(self, Serum) and (isinstance(other, Genome)):
            return True
        else:
            return False

    def _generate_pseudo_sample_id(self, original_sample_id, pseudo_sample_path):
        data = {"samples":[]}
        if os.path.exists(pseudo_sample_path):
            with open(pseudo_sample_path, 'r') as json_file:
                data = json.load(json_file)
                pseudo_list = data["samples"]
        else:
            pseudo_list = []

        existing_ids = [val["sample_ID"] for val in pseudo_list]
        if original_sample_id not in existing_ids:
            pseudoID = "mmci_sample_" + str(uuid.uuid4())
            with open(pseudo_sample_path, 'w+') as outfile:
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

class Tissue(Material):
    
    def __init__(self, lts_child, pseudo_number, sample_table):
        super().__init__(lts_child, pseudo_number, sample_table)
        self.material = "tissue"
        self.pTNM = lts_child.find(f"{super().xml_prefix}pTNM").text
        self.morphology = lts_child.find(f"{super().xml_prefix}morphology").text
        self.diagnosis = lts_child.find(f"{super().xml_prefix}diagnosis").text
        self.cutTime = lts_child.find(f"{super().xml_prefix}cutTime").text
        self.freezeTime = lts_child.find(f"{super().xml_prefix}freezeTime").text
        self.retrieved = lts_child.find(f"{super().xml_prefix}retrieved").text

class Serum(Material):

    def __init__(self, lts_child, pseudo_number,  sample_table):
        super().__init__(lts_child, pseudo_number,  sample_table)
        self.material = "serum"
        self.diagnosis = lts_child.find(f"{super().xml_prefix}diagnosis").text
        self.takingDate = lts_child.find(f"{super().xml_prefix}takingDate").text

class Genome(Material):

    def __init__(self, lts_child, pseudo_number,  sample_table):
        super().__init__(lts_child, pseudo_number,  sample_table)
        self.material = "genome"
        self.takingDate = lts_child.find(f"{super().xml_prefix}takingDate").text

class Patient:

    def __init__(self, id: str, birth: str, sex: str, samples: list[Material]):
        self.ID = id
        self.birth = birth
        self.sex = sex
        self.samples = samples

    def __eq__(self, other):
        if isinstance(other, Patient):
            return self.ID == other.ID
        return False


class FindClinicalInfo:
    
    def __init__(self, bbm_export_folder_path: str, predictive_numbers: list[str],
                 pseudo_tables_path: str, run_path: str):
        self.export_path = bbm_export_folder_path
        self.predictive_numbers = predictive_numbers
        self.pseudo_pred_table_path = os.path.join(pseudo_tables_path, "predictive.json")
        self.pseudo_patient_table_path = os.path.join(pseudo_tables_path, "patients.json")
        self.pseudo_sample_table_path = os.path.join(pseudo_tables_path, "samples.json")
        self.run_path = run_path
        self.pseudo_ids = []

    def __call__(self):
        clinical_data = self._collect_clinical_data()
        clinical_info_path = os.path.join(self.run_path, "clinical_info.json")
        with open(clinical_info_path, "w") as f:
            json.dump(self._convert_collection_to_dict(clinical_data), f, indent=4)
        
        for patient in clinical_data:
            pac_dict = self._convert_samples_to_dict(patient).__dict__
            clinical_info_path = os.path.join(self.run_path, "clinical_info_per_patient", f"{pac_dict['ID']}.json")
            if not os.path.exists(os.path.join(self.run_path, "clinical_info_per_patient")):
                os.mkdir(os.path.join(self.run_path, "clinical_info_per_patient"))
            
            with open(clinical_info_path, "w") as f:
                json.dump(pac_dict, f, indent=4)

            patient.samples = self._get_samples_with_unique_predictive_number(patient.samples)
            pac_dict_for_catalogue = self._convert_samples_to_dict(patient).__dict__
            catalog_info_path = os.path.join(self.run_path,
                                            "catalog_info_per_patient",
                                            f"{pac_dict_for_catalogue['samples'][0]['pseudo_id']}.json")
            if not os.path.exists(os.path.join(self.run_path, "catalog_info_per_patient")):
                os.mkdir(os.path.join(self.run_path, "catalog_info_per_patient"))
            
            with open(catalog_info_path, "w") as f:
                json.dump(pac_dict_for_catalogue, f, indent=4)


    def get_pseudo_ids(self) -> list[str]:
        return self.pseudo_ids

    def _get_samples_with_unique_predictive_number(self, samples):
        unique = []
        is_unique = True
        for sample in samples:
            for sample_unique in unique:
                if sample.pseudo_id == sample_unique.pseudo_id:
                    is_unique = False
            if is_unique:
                unique.append(sample)

        return unique

    def _collect_clinical_data(self) -> list[Patient]:
        collection = []
        for pred_number in self.predictive_numbers:
            pseudo_id = self._add_pseudo_ID(pred_number)
            self.pseudo_ids.append(pseudo_id)
            collection += self._check_for_predictive_number_in_export(pred_number, pseudo_id)
        
        collection = self._combine_patients_with_same_id(collection)
        collection = self._remove_duplicates_from_list_and_sort_samples(collection)
        return collection

    def _remove_duplicates_from_list_and_sort_samples(self, patient_list):
        for patient in patient_list:
            samples = list(set(patient.samples))
            patient.samples = sorted(samples)

        return patient_list

    def _combine_patients_with_same_id(self, collection):
        combined_collection = []
        for i in range(len(collection)):
            for y in range(len(collection)):
                    if y != i and collection[i] == collection[y] and collection[i] not in combined_collection:
                        patient_connected = collection[i]
                        patient_connected.samples += collection[y].samples
                        combined_collection.append(patient_connected)
                    elif y != i and collection[i] != collection[y] and collection[i] not in combined_collection:
                        patient_connected = collection[i]
                        combined_collection.append(patient_connected)
        return combined_collection

    def _convert_collection_to_dict(self, collection: list[Patient]) -> list[dict]:
        patient_dicts = [self._convert_samples_to_dict(patient).__dict__ for patient in collection]
        return {"clinical_data": patient_dicts}

    def _convert_samples_to_dict(self, patient):
        patient_copy = copy.deepcopy(patient)
        patient_copy.samples = [sample.__dict__ for sample in patient_copy.samples]
        return patient_copy

    def _add_pseudo_ID(self, original_ID):
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
        if os.path.exists(self.pseudo_pred_table_path):
            with open(self.pseudo_pred_table_path, 'r') as json_file:
                data = json.load(json_file)
                pseudo_list = data["predictive"]
        else:
            pseudo_list = []                                 
        
        existing_ids = [val["predictive_number"] for val in pseudo_list]
        if original_ID not in existing_ids:                  
            pseudoID = "mmci_predictive_" + str(uuid.uuid4())
            with open(self.pseudo_pred_table_path, 'w+') as outfile:
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


    def _check_for_predictive_number_in_export(self, predictive_number, pseudo_number):
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
            lts = root.find(f"{Material.xml_prefix}LTS")
            found_predictive = False
            sample_data = []
            for child in lts:
                if ("/" in child.attrib["predictive_number"] and
                self._fix_predictive_number(child.attrib["predictive_number"]) == predictive_number):
                    found_predictive = True
                    if "tissue" in child.tag:
                        sample_data.append(Tissue(child, pseudo_number, self.pseudo_sample_table_path))
                    if "genome" in child.tag:
                        sample_data.append(Genome(child, pseudo_number, self.pseudo_sample_table_path))
                    if "serum" in child.tag:
                        sample_data.append(Serum(child, pseudo_number, self.pseudo_sample_table_path))

            if found_predictive:
                patient = Patient(
                    self._generate_pseudo_patient_id(root.get("id")),
                    f"{root.get('month')}/{root.get('year')}",
                    root.get("sex"),
                    sample_data
                )
                clinical_data.append(patient)

        return clinical_data

    def _fix_predictive_number(self, predictive_number):
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
        part1 = predictive_number.split("/")[0][2:]
        part2 = predictive_number.split("/")[1]
        predictive_formated = f"{part2}-{part1}"
        return predictive_formated

    def _generate_pseudo_patient_id(self, original_ID):
        data = {"patients":[]}
        if os.path.exists(self.pseudo_patient_table_path):
            with open(self.pseudo_patient_table_path, 'r') as json_file:
                data = json.load(json_file)
                pseudo_list = data["patients"]
        else:
            pseudo_list = []

        existing_ids = [val["patient_ID"] for val in pseudo_list]
        if original_ID not in existing_ids:
            pseudoID = "mmci_patient_" + str(uuid.uuid4())
            with open(self.pseudo_patient_table_path, 'w+') as outfile:
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