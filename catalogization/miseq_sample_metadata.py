import json
import sys
import re


class SampleInfoMMCI:

    def __init__(self):
        self.idSample: str = ''          #clinical_info.json (pseudoID: "mmci_predictive_44d8480d-d2d4-44f9-aefe-7ace74329f7a")
        self.collFromPerson: str = ''
        self.belToDiag: str = ''
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
    sample.idSample = data.get('clinical_data')[0].get('Samples')[0].get('pseudoID')
    sample.collFromPerson = data.get('clinical_data')[0].get('ID')
    sample.samplTimestamp = data.get('clinical_data')[0].get('Samples')[0].get('takingDate')
    #sample.regTimestamp = data.get('clinical_data')[0].get('Samples')[0].get('freezeTime')
    #sample.bioSpeciType =
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
