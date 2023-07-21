import molgenis.client
import json

class MolgenisImporter:

    def __init__(self, clinical_json, run_metadata_json):
        #self.session = molgenis.client.Session("https://data.bbmri.cz")
        #self.session.login("***********", "************")
        self.clinical = self.extract_personal(self.load_json_to_dict(clinical_json))
        self.run_mtdt = self.extract_personal(self.load_json_to_dict(run_metadata_json))

    def __call__(self):
        self.session.logout()

    def load_json_to_dict(self, path):
        with open(path, "r") as f:
            d = json.load(f)

        return d
    
    def get_clinical_data(self, export_data):
        if export_data["material"] == "tissue":
            export_data = {
                "pTNM":export_data["pTNM"],
                "morphology":export_data["morphology"],
                "diagnosis":export_data["diagnosis"],
            }
        elif export_data["material"] == "serum":
            export_data = {
                "diagnosis":export_data["diangosis"],
                "pTNM": None,
                "morphology": None,
            }
        elif export_data["material"] == "genome":
            export_data = {
                "diagnosis": None,
                "pTNM": None,
                "morphology": None,
            }
        else:
            export_data = {
                "diagnosis": None,
                "pTNM": None,
                "morphology": None,
            }

            return export_data

    def get_sample_data(self, export_data):
        #TODO
        pass

    def extract_and_add_personal(self, clinical_dict):
        for patient in clinical_dict:
            print(patient["ID"], patient["Birth"].split("/")[1], patient["Sex"])
            for clinical in patient["Samples"]:
                print(self.get_various_unique_clinical_data(clinical))

    def add_personal(self, id, sex, year_of_birth):
        self.session.add('fair-genomes_personal',
                    personalidentifier= "015",
                    phenotypicsex="female",
                    genotypicsex= "",
                    countryofresidence= "Czechia",
                    ancestry= "",
                    countryofbirth="Czechia",
                    yearofbirth="1989",
                    inclusionstatus= "Alive",
                    primaryaffiliatedinstitute="Masaryk Memorial Cancer Institute",
                    resourcesinotherinstitutes= "",
                    participatesinstudy= "")
    
    def extract_and_add_clinical(self):
        pass

    def add_clinical(self):
        self.session.add('fair-genomes_clinical')

    def add_sequencing(self):
        self.session.add("fair-genomes_sequencing",
                    sequencingidentifier="0043/9",
                    sequencingplatform="Illumina platform",
                    sequencinginstrumentmodel= "MiSeq",
                    sequencingmethod= "Sequencing by Synthesis",
                    averagereaddepth= "",
                    observedreadlength="101",
                    observedinsertsize= "",
                    otherqualitymetrics= "Cluster Density 149.921371; Clusters Passing Filter 92.21017; Estimated Yield \n76.7622452; Error Description NA; Num Lanes 4; Flowcell ID HC2G2BGXH\n")
    
    def add_sample_preparation(self):
        self.session.add("fair-genomes_samplepreparation",
                    sampleprepidentifier= "sampleprep_A2020/15",
                    belongstomaterial= "mmci_XXXXXXXXXXXX",
                    inputamount= "15",
                    librarypreparationkit="Accel\u2122  Amplicon  Custom Core  Kit ",
                    pcrfree="false",
                    targetenrichmentkit= "Accel\u2122  Amplicon  Custom Core  Kit",
                    umispresent= "false",
                    intendedinsertsize= "265",
            intendedreadlength= "282")