import xml.etree.ElementTree as ET
import json
import sys
from datetime import date
import re
import argparse
import os

#script can be run by command: python miseq_run_metadata.py -r path/to/organised/run  
class RunInfoMMCI:

    def __init__(self):
        self.idMMCI: int = 0            #XML_RunParameters
        self.seqDate: str = ''          #XML_RunParameters
        self.seqPlatform: str = ''      #always "Illumina platform"
        self.seqModel: str = ''         #MiSeq
        self.seqMethod: str = ''        #always "Illumina Sequencing"
        #self.avReadDepth: str = ''      #[predictive number]_StatInfo.txt - FILE PER ONE SAMPLE FROM ANALYSIS
        #self.obsReadLength: str = ''    #[predictive number]_StatInfo.txt - FILE PER ONE SAMPLE FROM ANALYSIS
        self.percentageQ30: int = ''    #AnalysisLog.txt
        self.percentageTR20: str = ''   #this number is not relevant for MMCI
        self.clusterPF: int = 0         #GemerateFASTQRunStatistics
        self.numLanes: int = 0          #XML_RunParameters
        self.flowcellID: str = ''       #XML_RunInfo

class CollectRunMetadata:

    def __init__(self, run_path):
        self.run_info = RunInfoMMCI()
        self.run_path = run_path

    def __call__(self):
        xml_runParameters = os.path.join(self.run_path, "runParameters.xml")
        xml_GenerateFASTQRunStatistics = os.path.join(self.run_path, "GenerateFASTQRunStatistic.xml")
        xml_runInfo = os.path.join(self.run_path, "RunInfo.xml")
        txt_analysisLog = os.path.join(self.run_path, "AnalysisLog.txt")

        run_data = self.find_run_metadata(xml_runParameters, xml_GenerateFASTQRunStatistics, xml_runInfo, txt_analysisLog)
        run_metadata = os.path.join(self.run_path, "run_metadata.json")

        with open(run_metadata, 'w') as outfile:
            json.dump(run_data, outfile, indent=4)

    def find_run_metadata(self, first_source, second_source, third_source, fourth_source): #fifth_source
        tree1 = ET.parse(first_source)
        self.run_info = self.find_el_in_runparam(tree1, self.run_info)
        tree2 = ET.parse(second_source)
        self.run_info = self.find_el_in_generateFASTQrunstatistics(tree2, self.run_info)
        tree3 = ET.parse(third_source)
        self.run_info= self.find_el_in_runinfo(tree3, self.run_info)
        self.run_info= self.find_el_in_analysislog(fourth_source, self.run_info)
        jsonStr = self.run_info.__dict__
        return jsonStr

    def find_el_in_runparam(self, tree1, run):          #this function extracts run parameters from file "RunParameters"
        for element in tree1.iter("RunParameters"):
            run.idMMCI = "mis_" + element.find("RunNumber").text
            run_date = element.find("RunStartDate").text
            year = 2000 + int(run_date[:2])  # prekonvertovanie roku do celého čísla
            month = int(run_date[2:4])
            day = int(run_date[4:])
            d = date(year, month, day)
            isoformat = d.isoformat()
            run.seqDate = isoformat
            run.seqPlatform = "Illumina platform"
            run.seqMethod = "Illumina Sequencing"
            run.seqModel = "MiSeq"
        for element in tree1.iter("Setup"):
            run.numLanes = element.find("NumLanes").text
        return run

    def find_el_in_generateFASTQrunstatistics(self, tree2, run): #this function extracts run parameters from file "GenerateFASTQRunStatistics"
        for element in tree2.iter("RunStats"):
            run.clusterPF = element.find("NumberOfClustersPF").text
        run.percentageTR20 = "NA"
        return run


    def find_el_in_runinfo(self, tree3, run):  #this function extracts run parameters from file "RunInfo"
        for element in tree3.iter("Run"):
            run.flowcellID = element.find("Flowcell").text
        return run

    def find_el_in_analysislog(self, txt_analysisLog, run): #this function extracts run parameters from file "AnalysisLog.txt"
        with open(txt_analysisLog, 'r') as f:
            for line in f:
                match = re.search(r'Percent >= Q30: ([\d]{1,2}.[\d]{1,2}\%)', line)
                if match:
                    run.percentageQ30 = match.group(1)
        return run

    def find_el_in_statinfo(self, txt_statInfo, run): #this function extracts run parameters from file "[predictive number]_StatInfo.txt"
        with open(txt_statInfo, 'r') as f:
            for line in f:
                match1 = re.search(r'Average Read Length: ([\d]+)', line)
                if match1:
                    run.obsReadLength = match1.group(1)
                match2 = re.search(r'Average Coverage: ([\d]+)', line)
                if match2:
                    run.avReadDepth = match2.group(1)
        return run
