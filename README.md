# NGS-data-FAIRification
Integration and cataloguing of biobanking and clinical data using FAIR Genomes Metadata Schema.

## Code parts
The following folder contain various codes to process Sequencing runs

- pseudonymization
  - pseudonymize_pipeline.sh
  - remove_files.sh
  - [pseudonymization.py](#pseudonymizationpy)
  - replace_predictive.sh
- extraction_script
  - miseq_run_metadata.py
  - nextseq_run_metadata.py

#### pseudonymization.py 
This script pseudonymizes majority of the Sequencing run, mainly the file names and SampleSheet
Also it collects data from BBM exports and connects them to the Sequencing run.

**Script organisation**
1. pseudonymize_run
	1. pseudo_sample_sheet
		1. add_pseudo_ID
		3. check_for_predictive_in_export
			1. fix_predictive_number
			2. prepare_tissue
			3. prepare_serum
			4. prepare_genome
	2. save_clinical_files
		1. remove_duplicate_dicts
	3. create_temporary_pseudo_table
	4. locate_all_files_with_predictive_number
		1. rename_files_recursively (this is run recursively)
