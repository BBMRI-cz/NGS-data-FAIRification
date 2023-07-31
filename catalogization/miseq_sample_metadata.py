import xml.etree.ElementTree as ET
import json
import sys
from datetime import date
import re
import argparse
import os

#script can be run by command: python miseq_sample_metadata.py -r path/to/sample/files
#files needed for this script:
#[predictive number]_StatInfo.txt
#clinical_info.json
class SampleInfoMMCI:

    def __init__(self):
        self.idSample: int = 0          #clinical_info.json (pseudoID: "mmci_predictive_44d8480d-d2d4-44f9-aefe-7ace74329f7a")
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

class CollectSampleMetadata:

    def __init__(self, sample_path):
        self.sample_info = SampleInfoMMCI()
        self.sample_path = sample_path

    def __call__(self):
        txt_statInfo = os.path.join(self.sample_path, "StatInfo.txt")
        json_clinical_info = os.path.join(self.sample_path, "clinical_info.json")


        sample_data = self.find_sample_metadata(txt_statInfo, json_clinical_info)
        sample_metadata = os.path.join(self.sample_path, "sample_metadata.json")

        with open(sample_metadata, 'w') as outfile:
            json.dump(sample_data, outfile, indent=4)

    def find_sample_metadata(self, first_source, second_source):
        tree1 = ET.parse(first_source)
        self.sample_info = self.find_el_in_runparam(tree1, self.run_info)
        tree2 = ET.parse(second_source)
        self.sample_info = self.find_el_in_generateFASTQrunstatistics(tree2, self.run_info)
        jsonStr = self.sample_info.__dict__
        return jsonStr



    def find_el_in_statinfo(self, txt_statInfo, sample): #this function extracts run parameters from file "[predictive number]_StatInfo.txt"
        with open(txt_statInfo, 'r') as f:
            for line in f:
                match1 = re.search(r'Average Read Length: ([\d]+)', line)
                if match1:
                    sample.obsReadLength = match1.group(1)
                match2 = re.search(r'Average Coverage: ([\d]+)', line)
                if match2:
                    sample.avReadDepth = match2.group(1)
        return sample
