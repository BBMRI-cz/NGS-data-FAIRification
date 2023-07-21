from organise_run import RunOrganiser
from miseq_run_metadata import CollectRunMetadata
from import_metadata import MolgenisImporter
import argparse
import os

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
    prog="Organiser",
    description="Organise pseudonymized runs into a specifed output folder")

    parser.add_argument("-r", "--runs", type=str, required=True, help="Path to sequencing run path that will be pseudonymized")
    parser.add_argument("-o", "--output", type=str, required=True, help="Path to the organise file")
    parser.add_argument("-p", "--patients", type=str, required=True, help="Path to a patient folder")

    args = parser.parse_args()

    for file in os.listdir(args.runs):
        run_path = RunOrganiser(args.runs, file, args.output, args.patients)()
        CollectRunMetadata(os.path.join(args.output, run_path))()
        MolgenisImporter(os.path.join(args.output, run_path, "clinical_info.json"), os.path.join(args.output, run_path, "run_metadata.json"))

