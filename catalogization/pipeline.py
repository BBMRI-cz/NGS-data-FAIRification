from organise_run import RunOrganiser
from miseq_run_metadata import CollectRunMetadata
from miseq_sample_metadata import CollectSampleMetadata
from import_metadata import MolgenisImporter
import argparse
import os

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
    prog="Organiser",
    description="Organise pseudonymized runs into a specifed output folder \n. It is important to use full paths")

    parser.add_argument("-r", "--runs", type=str, required=True, help="Path to sequencing run path that will be pseudonymized")
    parser.add_argument("-o", "--output", type=str, required=True, help="Path to the organise file")
    parser.add_argument("-p", "--patients", type=str, required=True, help="Path to a patient folder")

    args = parser.parse_args()

    for file in os.listdir(args.runs):
        run_path = RunOrganiser(args.runs, file, args.output, args.patients)()
        CollectRunMetadata(os.path.join(args.output, run_path))()
        print("Run:", os.path.join(args.output, run_path))
        clinical_info = os.path.join(args.output, run_path, "catalog_info_per_patient")
        print("Clinical info:", clinical_info)
        for sample in os.listdir(os.path.join(args.output, run_path, "catalog_info_per_patient")):
            sample = sample.replace(".json", "")
            sample_stat_info = os.path.join(os.path.join(args.output, run_path), "Samples", sample, "Analysis", "Reports", f"{sample}_StatInfo.txt")
            print("sample_stat_info:", sample_stat_info)
            print(sample)
            CollectSampleMetadata(os.path.join(args.output, run_path), sample_stat_info, clinical_info)()
        #MolgenisImporter(os.path.join(args.output, run_path, "clinical_info.json"), os.path.join(args.output, run_path, "run_metadata.json"))