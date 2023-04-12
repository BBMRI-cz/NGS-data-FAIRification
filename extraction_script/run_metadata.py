import xml.etree.ElementTree as ET
import json
import PyPDF2
import sys


class RunInfoMMCI:

    def __init__(self):
        self.idMMCI: int = 0            #XML_RunParameters
        self.seqDate: str = ''          #XML_RunParameters
        self.seqPlatform: str = ''      #always "Illumina platform" while NextSeq/MiSeq
        self.seqModel: str = ''         #NextSeq 550 / MiSeq
        self.seqMethod: str = ''        #always "Illumina Sequencing" while NextSeq/MiSeq
        #self.avReadDepth: str = '' - location in progress
        #self.obsReadLength: str = '' - location in progress
        self.obsInsertSize: int = 0     #QC Metrics Report - Trusight Oncology 500 (pdf)
        #self.percentageQ30: float = 0 - location in progress
        self.clusterDensity: float = 0  #XML_RunCompletionStatus
        self.clusterPF: float = 0       #XML_RunCompletionStatus
        self.estimatedYield: float = 0  #XML_RunCompletionStatus
        self.errorDescription: str = '' #XML_RunCompletionStatus
        self.numLanes: int = 0          #XML_RunParameters
        self.flowcellID: str = ''       #XML_RunInfo

def find_el_in_runparam(tree1, run):          #this function extracts run parameters from file "RunParameters"
    for element in tree1.iter("RunParameters"):
        run.idMMCI = element.find("RunNumber").text
        run.seqDate = element.find("RunStartDate").text
        if "Illumina" in element.find("RecipeFolder").text:
            run.seqPlatform = "Illumina platform"
            run.seqMethod = "Illumina Sequencing"
        if element.find("InstrumentID").text.startswith("N"):
            run.seqModel = "NextSeq 500"
        if element.find("InstrumentID").text.startswith("M"):
            run.seqModel = "MiSeq"
    for element in tree1.iter("Setup"):
        run.numLanes = element.find("NumLanes").text
    return run


def find_el_in_runcomplstatus(tree2, run):   #this function extracts run parameters from file RunCompletionStatus
    for element in tree2.iter("RunCompletionStatus"):
        run.clusterDensity = element.find("ClusterDensity").text
        run.clusterPF = element.find("ClustersPassingFilter").text
        run.estimatedYield = element.find("EstimatedYield").text
        run.errorDescription = element.find("ErrorDescription").text
    return run


def find_el_in_runinfo(tree3, run):
    for element in tree3.iter("Run"):
        run.flowcellID = element.find("Flowcell").text
    return run

def between(value, a, b):
    pos_a = value.find(a)
    if pos_a == -1: return ""
    pos_b = value.find(b)
    if pos_b == -1: return ""
    adjust_pos_a = pos_a + len(a)
    if adjust_pos_a >= pos_b: return ""
    return value[adjust_pos_a: pos_b]

def find_el_in_pdf(pdf_file, run):
    with open(pdf_file, "rb") as file:
        pdfFileReader = PyPDF2.PdfReader(file)
        pages = pdfFileReader.pages[0]
        text = pages.extract_text()
        desired = between(text, "MEDIAN_INSERT_SIZE (bp)", ">= 70")
    run.obsInsertSize = desired
    return run


def find_run_metadata(first_source, second_source, third_source, pdf_file):
    run = RunInfoMMCI()
    tree1 = ET.parse(first_source)
    run = find_el_in_runparam(tree1, run)
    tree2 = ET.parse(second_source)
    run = find_el_in_runcomplstatus(tree2, run)
    tree3 = ET.parse(third_source)
    run = find_el_in_runinfo(tree3, run)
    run = find_el_in_pdf(pdf_file, run)
    jsonStr = json.dumps(run.__dict__)
    return jsonStr


if __name__ == "__main__":
    xml_runParameters = sys.argv[1]
    xml_runCompletionStatus = sys.argv[2]
    xml_runInfo = sys.argv[3]
    pdf_file = sys.argv[4]

    data = find_run_metadata(xml_runParameters, xml_runCompletionStatus, xml_runInfo, pdf_file)
    with open('run_metadata.json', 'w') as outfile:
        outfile.write(data)

