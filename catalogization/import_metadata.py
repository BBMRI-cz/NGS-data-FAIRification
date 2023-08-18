import molgenis.client
import json
import os

class Personal:

    def __init__(self, patient_dict):
        self.personalidentifier= patient_dict["ID"],
        self.phenotypicsex = patient_dict["sex"],
        self.genotypicsex = None,
        self.selfcountryofresidence = "Czechia",
        self.ancestry = "",
        self.countryofbirth = "Czechia",
        self.yearofbirth = patient_dict["birth"].split("/")[1]
        self.inclusionstatus = "Alive",
        self.primaryaffiliatedinstitute = "Masaryk Memorial Cancer Institute",
        self.resourcesinotherinstitutes = "",
        self.participatesinstudy= ""

class Clinical:
    def __init__(self, patient_dict):
        sample = patient_dict["samples"][0]
        self.clinicalidentifier = patient_dict["ID"].replace("patient", "clinical"),
        self.belongstoperson = patient_dict["ID"]
        self.phenotype = None
        self.unobservedphenotype = None
        self.phenotypicdataavailable = None
        self.clinicaldiagnosis = sample["diagnosis"] if sample["material"] != "genome" else None
        self.moleculardiagnosisgene = None
        self.moleculardiagnosisother = None
        self.ageatdiagnosis = self._calculate_age_at_diagnosis(patient_dict["birth"].split("/")[1], sample)
        self.ageatlastscreening = None
        self.medication = None
        self.drugregimen = None
        self.familymembersaffected = None
        self.familymemberssequenced = None
        self.consanguinity = None
        self.medicalhistory = None
        self.ageofonset = self._calculate_age_at_diagnosis(patient_dict["birth"].split("/")[1], sample)
        self.firstcontact = None
        self.functioning = None
        self.materialusedindiagnosis = None # Here could be something

    def _calculate_age_at_diagnosis(self, birth, sample):
        if sample["material"] == "tissue":
            return int(sample["freezeTime"].split("-")[0]) - int(birth)
        else:
            return int(sample["takingDate"].split("-")[0]) - int(birth)

class Material:

    def __init__(self, patient_dict, sample_dict):
        sample =  patient_dict["samples"][0]
        self.materialidentifier = sample["sample_ID"]
        self.collectedfromperson = patient_dict["ID"]
        self.belongstodiagnosis = patient_dict["ID"].replace("patient", "clinical"),
        self.samplingtimestamp = sample["cutTime"]
        self.registrationtimestamp = sample["freezeTime"]
        self.samplingprotocol = None
        self.samplingprotocoldeviation = None
        self.reasonforsamplingprotocoldeviation = None
        self.biospecimentype = sample_dict["bioSpeciType"]
        self.anatomicalsource = None
        self.pathologicalsate = sample_dict["pathoState"]
        self.storageconditions = sample_dict["storCond"] 
        self.expirationdate = None
        self.percentagetumourcells = None
        self.physicallocation = "FFPE blocks at Department of Oncological Pathology MMCI" #TODO
        self.derivedfrom = None
        self.wholeslideimagesavailability = False #TODO
        self.radiotherapyimagesavailability	= False #TODO

class SamplePreparation:

    def __init__(self, patient_dict):
        sample = patient_dict["samples"][0]
        self.sampleprepidentifier= sample["pseudo_id"].replace("predictive", "sampleprep")
        self.belongstomaterial= sample["sample_ID"]

        # TODO
        self.inputamount= "15",
        self.librarypreparationkit="Accel\u2122  Amplicon  Custom Core  Kit ",
        self.pcrfree="false",
        self.targetenrichmentkit= "Accel\u2122  Amplicon  Custom Core  Kit",
        self.umispresent= "false",
        self.intendedinsertsize= "265",
        self.intendedreadlength= "282"
        # TODO

class Sequencing:
    def __init__(self, patient_dict, sample_dict, run_metadata_dict):
        sample = patient_dict["samples"][0]
        self.sequencingidentifier = sample["pseudo_id"]
        self.belongstosample = sample["pseudo_id"].replace("predictive", "sampleprep")
        self.sequencingdate = run_metadata_dict["seqDate"]
        self.sequencingplatform = run_metadata_dict["seqPlatform"]
        self.sequencinginstrumentmodel = run_metadata_dict["seqModel"]
        self.sequencingmethod = run_metadata_dict["seqMethod"]
        self.averagereaddepth = sample_dict["avReadDepth"]
        self.observedreadlength = sample_dict["obsReadLength"]
        self.observedinsertsize = None
        self.percentageq30 = run_metadata_dict["percentageQ30"]
        self.percentagetr20 = run_metadata_dict["percentageTR20"]
        self.otherqualitymetrics = None # TODO

class Analysis:
    def __init__(self, patient_dict):
        sample = patient_dict["samples"][0]
        self.analysisidentifier = sample["pseudo_id"].replace("predictive", "analysis")
        self.belongstosequencing = sample["pseudo_id"]
        self.physicaldatalocation = "Masaryk Memorial Cancer Istitute"
        self.abstractdatalocation = "Sensitive Cloud Institute of Computer Science"
        self.dataformatsstored = ".fastq, VCF"
        self.algorithmsused = "" # TODO
        self.referencegenomeused = None
        self.bioinformaticprotocolused = None
        self.bioinformaticprotocoldeviation = None
        self.reasonforbioinformaticprotocoldeviation = None
        self.wgsguidelinefollowed = None


class MolgenisImporter:

    def __init__(self, catalog_info, samples_metadata, run_metadata):
        self.session = molgenis.client.Session("https://data.bbmri.cz")
        self.session.login("*********", "*********")
        self.catalog_info_folder = catalog_info
        self.samples_metadata_folder = samples_metadata
        with open(run_metadata, "r") as f:
            self.run_metadata = json.load(f)

    def __call__(self):
        for pred_number in os.listdir(self.catalog_info_folder):
            clinical_info_file = os.path.join(self.catalog_info_folder, pred_number)
            print(clinical_info_file)
            with open(clinical_info_file, "r") as f:
                clinical_info_file = json.load(f)

            sample_metadata_file = os.path.join(self.samples_metadata_folder, pred_number)
            with open(sample_metadata_file, "r") as f:
                sample_metadata_file = json.load(f)

            personal = Personal(clinical_info_file)
            self.add_data(personal ,'fair-genomes_personal')
            
            clinical = Clinical(clinical_info_file)
            self.add_data(clinical, 'fair-genomes_clinical')

            material = Material(clinical_info_file, sample_metadata_file)
            self.add_data(material, 'fair-genomes_material')

            sample_preparation = SamplePreparation(clinical_info_file)
            self.add_data(sample_preparation, 'fair-genomes_samplepreparation')

            sequencing = Sequencing(clinical_info_file, sample_metadata_file, self.run_metadata)
            self.add_data(sequencing, 'fair-genomes_sequencing')

            analysis = Analysis(clinical_info_file)
            self.add_data(analysis, 'fair-genomes_analysis') 
            
            self.session.logout()

    def add_data(self, data, data_type):
        data_dict = data.__dict__
        self.session.add(data_type, **data_dict)
    