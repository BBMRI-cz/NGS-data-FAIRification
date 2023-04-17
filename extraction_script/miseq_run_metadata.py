import xml.etree.ElementTree as ET
import json
import sys
from datetime import date
import re

#script can be run by command: python miseq_run_metadata_extraction.py RunParameters.xml GenerateFASTQRunStatistics.xml RunInfo.xml AnalysisLog.txt 2022-2633_StatInfo.txt

class RunInfoMMCI:

    def __init__(self):
        self.idMMCI: int = 0            #XML_RunParameters
        self.seqDate: str = ''          #XML_RunParameters
        self.seqPlatform: str = ''      #always "Illumina platform"
        self.seqModel: str = ''         #MiSeq
        self.seqMethod: str = ''        #always "Illumina Sequencing"
        self.avReadDepth: str = ''      #[predictive number]_StatInfo.txt - FILE PER ONE SAMPLE FROM ANALYSIS
        self.obsReadLength: str = ''    #[predictive number]_StatInfo.txt - FILE PER ONE SAMPLE FROM ANALYSIS
        #self.obsInsertSize: int = 0    #
        self.percentageQ30: int = ''  #AnalysisLog.txt
        self.percentageTR20: str = ''  #this number is not relevant for MMCI
        #self.clusterDensity: float = 0  #
        self.clusterPF: int = 0       #GemerateFASTQRunStatistics
        #self.estimatedYield: float = 0  #
        #self.errorDescription: str = '' #
        self.numLanes: int = 0          #XML_RunParameters
        self.flowcellID: str = ''       #XML_RunInfo

def find_el_in_runparam(tree1, run):          #this function extracts run parameters from file "RunParameters"
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

def find_el_in_generateFASTQrunstatistics(tree2, run): #this function extracts run parameters from file "GenerateFASTQRunStatistics"
    for element in tree2.iter("RunStats"):
        run.clusterPF = element.find("NumberOfClustersPF").text
    run.percentageTR20 = "NA"
    return run


def find_el_in_runinfo(tree3, run):  #this function extracts run parameters from file "RunInfo"
    for element in tree3.iter("Run"):
        run.flowcellID = element.find("Flowcell").text
    return run

def find_el_in_analysislog(txt_analysisLog, run): #this function extracts run parameters from file "AnalysisLog.txt"
    with open('AnalysisLog.txt', 'r') as f:
        for line in f:
            match = re.search(r'Percent >= Q30: ([\d]{1,2}.[\d]{1,2}\%)', line)
            if match:
                run.percentageQ30 = match.group(1)
    return run

def find_el_in_statinfo(txt_statInfo, run): #this function extracts run parameters from file "[predictive number]_StatInfo.txt"
    with open('2022-2633_StatInfo.txt', 'r') as f:
        for line in f:
            match1 = re.search(r'Average Read Length: ([\d]+)', line)
            if match1:
                run.obsReadLength = match1.group(1)
            match2 = re.search(r'Average Coverage: ([\d]+)', line)
            if match2:
                run.avReadDepth = match2.group(1)
    return run


def find_run_metadata(first_source, second_source, third_source, fourth_source, fifth_source):
    run = RunInfoMMCI()
    tree1 = ET.parse(first_source)
    run = find_el_in_runparam(tree1, run)
    tree2 = ET.parse(second_source)
    run = find_el_in_generateFASTQrunstatistics(tree2, run)
    tree3 = ET.parse(third_source)
    run = find_el_in_runinfo(tree3, run)
    run = find_el_in_analysislog(fourth_source, run)
    run = find_el_in_statinfo(fifth_source, run)
    jsonStr = json.dumps(run.__dict__)
    return jsonStr


if __name__ == "__main__":
    xml_runParameters = sys.argv[1]
    xml_GenerateFASTQRunStatistics = sys.argv[2]
    xml_runInfo = sys.argv[3]
    txt_analysisLog = sys.argv[4]
    txt_statInfo = sys.argv[5]

    data = find_run_metadata(xml_runParameters, xml_GenerateFASTQRunStatistics, xml_runInfo, txt_analysisLog, txt_statInfo)
    with open('run_metadata.json', 'w') as outfile:
        outfile.write(data)
