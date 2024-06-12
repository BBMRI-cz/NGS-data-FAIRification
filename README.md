# NGS-data-FAIRification
Integration, cataloguing and management of biobanking and clinical data using FAIR Genomes Metadata Schema.

## Documents
This repository stores supplementary files that are intended to be published together with the paper "Integration, Cataloguing and Management of Biobanking and Clinical Data Using FAIR Genomes Metadata Schema". Those files are located in "documents" folder. 
1. Supplementary File 1 & 2 (folder mindmaps_of_sequencer_outputs): contains schemas created when mapping files inside sequencer's output to distinguish important files from those which can be removed.
2. Supplementary File 3, 4, 5 (folder metadata_catalogue_SW_review): contains files completed during the process of reviewing multiple cataloguing softwares when deciding which software to use in the project.
3. Supplementary File 6 (supplementary_file_7_schema_mapping.xlsx): Excel file containing one sheet per each module within FAIR Genomes Metadata schema with all parameters listed in this module. Every single parameter is then mapped to MMCI values with the exact location od this value within MMCI data sources.
4. Supplementary File 7 (supplementary_file_8_FAIR_evaluation.xlsx): Excel file containing the results of final evaluation of reached FAIRness using the FAIR Data Maturity Model.
5. Supplementary File 8 (supplementary_file_9_NGS_pipeline_flowchart.png): working version of flow chart scatched before the actual implementation of designed sequencing pipeline at MMCI.

## Code

Code of this project is separeted into two parts (repositories)
1. [Pseudonymisation](https://github.com/BBMRI-cz/data-catalogue-pseudonymisation)

This repository takes care of pseudonymisation and collecting clinical information from the BBM export
1. [Organiser](https://github.com/BBMRI-cz/data-catalogue-organiser)
 
This repository cleans up the genomic data and organises them for later use. Also it collects structured genomic data and metadata and uploads them to the FAIR Genomes Molgenis Catalogue.
