[![DOI](https://zenodo.org/badge/572450436.svg)](https://doi.org/10.5281/zenodo.10390517)
# Integration, cataloguing and management of biobanking and clinical data using FAIR Genomes Metadata Schema.
Welcome to the repository that presents our work at the Bank of Biological Material of Masaryk Memorial Cancer Institute. Our team has developed an advanced, semi-automated data pipeline designed to streamline and integrate data from various sources associated with the biobank and upload metadata do the [data.bbmri.cz](https://data.bbmri.cz/) catalogue.

![image](https://github.com/user-attachments/assets/8d5d91b7-91ee-4f2f-9f7a-da66dad0548f)


## Project Description

The goal of this project is to create a robust data pipeline capable of handling multiple data inputs from a range of sources, including:
- **Hospital Information System Exports**: structured clinical and personal patient data extracted directly from hospital systems.
- **Biobank Data**: information on biological samples stored in the biobank.
- **Associated Data Types**: includes sequencing data, radiological images, and histopathological reports.

### Key Features of the Pipeline
1. **Data Integration**: Combines diverse data types into a unified framework.
2. **Data Cleaning and Structuring**: Ensures data is thoroughly cleaned and organized into a sustainable format that facilitates analysis and research.
3. **Secure Storage**: Stores processed data securely, complying with relevant data protection standards using [SensitiveCloud](https://www.cerit-sc.cz/infrastructure-services/sensitivecloud) service provided by CERIT-SC.
4. **Metadata Extraction**: Extracts key metadata during processing and populate [FAIR Genomes Metadata schema](https://www.nature.com/articles/s41597-022-01265-x).
5. **Metadata Publication**: Publishes the extracted metadata to [data.bbmri.cz](https://data.bbmri.cz), ensuring accessibility and transparency.

This pipeline enhances data handling efficiency within the biobank environment and supports further research by providing well-structured, reliable data sets.

## Code - FAIRification pipeline

Code of this project is separeted into three main parts (repositories):
1. [Pseudonymiser](https://github.com/BBMRI-cz/data-catalogue-pseudonymisation)
   
  This repository takes care of pseudonymisation and collecting clinical information from the BBM export.

2. [Organiser](https://github.com/BBMRI-cz/data-catalogue-organiser)
   
  This repository cleans up the genomic data and organises them for later use. Also it collects structured genomic data and metadata.

3. [Uploader](https://github.com/BBMRI-cz/data-catalogue-uploader)
   
  This repository uploads collected metadata to the metadata catalogue [data.bbmri.cz](https://data.bbmri.cz/).
  
## Data Retrieval Application

The additional (forth) [Data Retrieval](https://github.com/BBMRI-cz/data-catalogue-data-retrieval) repository provides tools for retrieving data from the catalog or secure storage, enabling the re-identification of original identifiers using pseudonyms and facilitating the retrieval of pseudonymized data in de-pseudonymised form from protected storage.


This repository includes an application developed for the retrieval of data, available (requiring MMCI VPN connection) at [sequencing.int.mou.cz](http://sequencing.int.mou.cz). The application offers two main functionalities:

1. **Pathology Data Retrieval**  
   Accessible at [sequencing.int.mou.cz/pathology-data-retrieval](http://sequencing.int.mou.cz/pathology-data-retrieval), this tool is designed for the pathology department. Pathologists can input a predictive identifier that the application automatically converts into a pseudonym and vice versa. This feature enables the department to seamlessly retrieve pseudonymized data in its original, non-pseudonymized form.

2. **Sample Verification for Biobank Staff**  
   The second feature available at [sequencing.int.mou.cz/bbm-sequencing-upload](http://sequencing.int.mou.cz/bbm-sequencing-upload) supports biobank staff by allowing them to upload an Excel export containing sample information. The application checks each sample and appends information directly into the Excel file, indicating whether sequencing data is available for each sample.


## Links for Further Documentation

Internal Documentation
- https://gitlab.int.mou.cz/bbmri/sequencingdata - requiring MMCI VPN connection - contains documentation for servers BBMRI-ANON1 and BBMRI-KATALOG and its workflow
- https://gitlab.ics.muni.cz/groups/bbmri.cz/-/wikis/MMCI/Anon-server - requiring autentication and granted access -  contains documentation for BBMRI-ANON1 and SensitiveCloud connection 

## Documents
This repository stores supplementary files that are intended to be published together with the paper "Integration, Cataloguing and Management of Biobanking and Clinical Data Using FAIR Genomes Metadata Schema". Those files are located in "documents" folder. 
1. Supplementary File 1 & 2 (folder mindmaps_of_sequencer_outputs): contains schemas created when mapping files inside sequencer's output to distinguish important files from those which can be removed.
2. Supplementary File 3, 4, 5 (folder metadata_catalogue_SW_review): contains files completed during the process of reviewing multiple cataloguing softwares when deciding which software to use in the project.
3. Supplementary File 6 (supplementary_file_6_schema_mapping.xlsx): Excel file containing one sheet per each module within FAIR Genomes Metadata schema with all parameters listed in this module. Every single parameter is then mapped to MMCI values with the exact location od this value within MMCI data sources.
4. Supplementary File 7 (supplementary_file_7_NGS_pipeline_flowchart.png): working version of flow chart scatched before the actual implementation of designed sequencing pipeline at MMCI.
5. Supplementary File 8 (supplementary_file_8_FAIR_evaluation.xlsx): Excel file containing the results of final evaluation of reached FAIRness using the FAIR Data Maturity Model.


