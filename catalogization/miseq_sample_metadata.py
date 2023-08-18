import json
import sys
import re
import os

class SampleInfoMMCI:

    def __init__(self):
        self.idSample: str = ''          #clinical_info.json (pseudoID: "mmci_predictive_44d8480d-d2d4-44f9-aefe-7ace74329f7a")
        self.collFromPerson: str = '' #clinical_info.json (ID:mmci_patient_a8236c65-51c1-4626-b866-fbf9a79ca176
        self.belToDiag: str = '' #clinical_info.json (ID:mmci_patient_a8236c65-51c1-4626-b866-fbf9a79ca176
        self.samplTimestamp: str = '' #clinical_info.json - takingDate
        self.regTimestamp: str = ''  # clinical_info.json - freezeTime
        self.bioSpeciType: str = '' #clinical_info.json - material
        self.pathoState: str = '' #clinical_info.json - chosen according to MaterialType (pr. 53 - nádor, 54 - norma, 55 - meta)
        self.storCond: str = ''  # clinical_info.json - chosen according to MaterialType
        # self.percTumCell: str = '' #pravdepodobne bude v BAM súboroch z analýzy, tie ale neviem otvoriť - malo by to ísť pomocou knižnice pysam, subrpocess alebo samtools
        # self.physLoc: str = '' #
        self.wsiAvailability: bool = False #according to biopsy number
        self.radioDataAvailability: bool = False #according to accession number in export
        self.avReadDepth: str = ''  # [predictive number]_StatInfo.txt
        self.obsReadLength: str = ''  # [predictive number]_StatInfo.txt
        # self.obsInsSize: int = 0 #pravdepodobne bude v BAM súboroch z analýzy, tie ale neviem otvoriť - malo by to ísť pomocou knižnice pysam, subrpocess alebo samtools
        self.diagnosis: str = ''  # clinical_info.json

class CollectSampleMetadata:

    def __init__(self, run_path, sample_stat_info_path, catalog_info_path):
        self.sample_info = SampleInfoMMCI()
        self.run_path = run_path
        self.sample_path = sample_stat_info_path
        self.clinical_data_path = catalog_info_path

    def __call__(self):
        sample_id = os.path.basename(self.sample_path).replace("_StatInfo.txt", "")
        metadata = self.find_sample_metadata(sample_id)
        print(os.path.join(self.run_path, "catalog_info_per_pacient", sample_id))
        if not os.path.exists(os.path.join(self.run_path, "sample_metadata")):
            os.mkdir(os.path.join(self.run_path, "sample_metadata"))
        with open(os.path.join(self.run_path, "sample_metadata" ,f'{sample_id}.json'), "w+") as outfile:
            json.dump(metadata, outfile, indent=4)

    def find_sample_metadata(self, sample_id):
        self.find_el_in_statinfo(self.sample_path)
        self.find_el_in_clinical_info(self.clinical_data_path, sample_id)
        jsonStr = self.sample_info.__dict__
        return jsonStr

    def find_el_in_statinfo(self, txt_statInfo): #this function extracts run parameters from file "[predictive number]_StatInfo.txt"
        with open(txt_statInfo, 'r', encoding='utf-8', errors="ignore") as f:
            for line in f:
                match1 = re.search(r'Average Read Length: ([\d]+)', line)
                if match1:
                    self.sample_info.obsReadLength = match1.group(1)
                match2 = re.search(r'Average Coverage: ([\d]+)', line)
                if match2:
                    self.sample_info.avReadDepth = match2.group(1)

    def find_el_in_clinical_info(self, json_clinical_data, sample_id):
        if os.path.exists(os.path.join(json_clinical_data, f"{sample_id}.json")):
            with open(os.path.join(json_clinical_data, f"{sample_id}.json"), encoding='utf-8') as json_file:
                data = json.load(json_file)
                    
            self.sample_info.idSample = data.get('samples')[0].get('pseudo_id')
            self.sample_info.collFromPerson = data.get('ID')
            self.sample_info.belToDiag = self.sample_info.collFromPerson[:5] + "clinical" + self.sample_info.collFromPerson[12:]
            material = data.get('samples')[0].get('material_type')
            bbm_module = data.get('samples')[0].get('material')
            if bbm_module == "tissue":
                self.sample_info.samplTimestamp = data.get('samples')[0].get('cutTime')
                self.sample_info.regTimestamp = data.get('samples')[0].get('freezeTime')
            else:
                self.sample_info.samplTimestamp = data.get('Samples')[0].get('takingDate')
            self.sample_info.pathoState = "NoInformation (NI, nullflavor)"
            if material == "4" or material == "54":
                self.sample_info.pathoState = "Normal"
            if material == "1" or material == "2" or material == "3" or material == "5" or material == "53" or material == "55" or material == "56":
                self.sample_info.pathoState = "Tumor"
            if material == "1" or material == "2" or material == "3" or material == "4" or material == "5":
                self.sample_info.bioSpeciType = "Frozen Tissue"
                self.sample_info.storCond = "Cryotube 1–2mL Programmable freezing to &lt;-135°C"
            if material == "53" or material == "54" or material == "55" or material == "56":
                self.sample_info.bioSpeciType = "Cryopreserved Tissue"
            if material == "7":
                self.sample_info.bioSpeciType = "Cell Pellet"
                self.sample_info.storCond = "Cryotube 1–2mL Programmable freezing to &lt;-135°C"
            if material == "C" or material == "K" or material == "L" or material == "PD" or material == "SD" or material == "T":
                self.sample_info.bioSpeciType = "Serum or Plasma"
                self.sample_info.storCond = "Cryotube 1–2mL Programmable freezing to &lt;-135°C"
            if material == "gD":
                self.sample_info.bioSpeciType = "Blood DNA"
                self.sample_info.storCond = "PP tube 0.5–2mL (-35) to (-18)°C"
            if material == "PK":
                self.sample_info.bioSpeciType = "Peripheral Blood"
                self.sample_info.storCond = "PP tube 0.5–2mL (-35) to (-18)°C"
            if material == "PR":
                self.sample_info.bioSpeciType = "Tumor Cell Line"
                self.sample_info.storCond = "Cryotube 1–2mL Programmable freezing to &lt;-135°C"
            self.sample_info.diagnosis = data.get('samples')[0].get('diagnosis')