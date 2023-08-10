import json
import sys
import re


class SampleInfoMMCI:

    def __init__(self):
        self.idSample: str = ''          #clinical_info.json (pseudoID: "mmci_predictive_44d8480d-d2d4-44f9-aefe-7ace74329f7a")
        self.collFromPerson: str = '' #clinical_info.json (ID:mmci_patient_a8236c65-51c1-4626-b866-fbf9a79ca176
        self.belToDiag: str = ''#clinical_info.json (ID:mmci_patient_a8236c65-51c1-4626-b866-fbf9a79ca176
        self.samplTimestamp: str = '' #clinical_info.json - takingDate
        self.regTimestamp: str = ''  # clinical_info.json - freezeTime
        self.bioSpeciType: str = '' #clinical_info.json - material
        self.pathoState: str = '' #clinical_info.json - chosen according to MaterialType (pr. 53 - nádor, 54 - norma, 55 - meta)
        self.storCond: str = ''  # clinical_info.json - chosen according to MaterialType
        #    self.percTumCell: str = '' #pravdepodobne bude v BAM súboroch z analýzy, tie ale neviem otvoriť - malo by to ísť pomocou knižnice pysam, subrpocess alebo samtools
        # self.physLoc: str = '' #
        self.wsiAvailability: bool = False #according to biopsy number
        self.radioDataAvailability: bool = False #according to accession number in export
        self.avReadDepth: str = ''  # [predictive number]_StatInfo.txt
        self.obsReadLength: str = ''  # [predictive number]_StatInfo.txt
    #    self.obsInsSize: int = 0 #pravdepodobne bude v BAM súboroch z analýzy, tie ale neviem otvoriť - malo by to ísť pomocou knižnice pysam, subrpocess alebo samtools
        self.diagnosis: str = ''  # clinical_info.json


def find_el_in_statinfo(txt_statInfo, sample): #this function extracts run parameters from file "[predictive number]_StatInfo.txt"
    with open(txt_statInfo, 'r') as f:
        for line in f:
            match1 = re.search(r'Average Read Length: ([\d]+)', line)
            if match1:
                sample.obsReadLength = match1.group(1)
            match2 = re.search(r'Average Coverage: ([\d]+)', line)
            if match2:
                sample.avReadDepth = match2.group(1)
    return sample

def find_el_in_clinical_info(json_clinical_data, sample):  #
    with open(json_clinical_data) as json_file:
        data = json.load(json_file)
    sample.idSample = data.get('Samples')[0].get('pseudoID')
    sample.collFromPerson = data.get('ID')
    sample.belToDiag = sample.collFromPerson[:5] + "clinical" + sample.collFromPerson[12:]
    material = data.get('Samples')[0].get('materialType')
    bbm_module = data.get('Samples')[0].get('material')
    if bbm_module == "tissue":
        sample.samplTimestamp = data.get('Samples')[0].get('cutTime')
        sample.regTimestamp = data.get('Samples')[0].get('freezeTime')
    else:
        sample.samplTimestamp = data.get('Samples')[0].get('takingDate')
    sample.pathoState = "NoInformation (NI, nullflavor)"
    if material == "4" or material == "54":
        sample.pathoState = "Normal"
    if material == "1" or material == "2" or material == "3" or material == "5" or material == "53" or material == "55" or material == "56":
        sample.pathoState = "Tumor"
    if material == "1" or material == "2" or material == "3" or material == "4" or material == "5":
        sample.bioSpeciType = "Frozen Tissue"
        sample.storCond = "Cryotube 1–2mL Programmable freezing to &lt;-135°C"
    if material == "53" or material == "54" or material == "55" or material == "56":
        sample.bioSpeciType = "Cryopreserved Tissue"
    if material == "7":
        sample.bioSpeciType = "Cell Pellet"
        sample.storCond = "Cryotube 1–2mL Programmable freezing to &lt;-135°C"
    if material == "C" or material == "K" or material == "L" or material == "PD" or material == "SD" or material == "T":
        sample.bioSpeciType = "Serum or Plasma"
        sample.storCond = "Cryotube 1–2mL Programmable freezing to &lt;-135°C"
    if material == "gD":
        sample.bioSpeciType = "Blood DNA"
        sample.storCond = "PP tube 0.5–2mL (-35) to (-18)°C"
    if material == "PK":
        sample.bioSpeciType = "Peripheral Blood"
        sample.storCond = "PP tube 0.5–2mL (-35) to (-18)°C"
    if material == "PR":
        sample.bioSpeciType = "Tumor Cell Line"
        sample.storCond = "Cryotube 1–2mL Programmable freezing to &lt;-135°C"
    sample.diagnosis = data.get('Samples')[0].get('diagnosis')
    return sample


def find_sample_metadata(first_source, second_source):
    sample = SampleInfoMMCI()
    sample = find_el_in_statinfo(first_source, sample)
    sample = find_el_in_clinical_info(second_source, sample)
    jsonStr = json.dumps(sample.__dict__)
    return jsonStr

txt_statInfo = sys.argv[1]
json_clinical_data = sys.argv[2]


metadata = find_sample_metadata(txt_statInfo, json_clinical_data)
with open('sample_metadata.json', 'w') as outfile:
    json.dump(metadata, outfile, indent=6)
