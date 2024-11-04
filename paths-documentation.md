# Paths Documentation - Important Folder Names

This document outlines the important paths to folders and provides a brief description of the contents within each folder used within the scripts.

## BBMRI-ANON1 Server

### Important Folders
- **/seq** - The SEQ directory on the BBMRI-ANON1 server is accessible via Samba from the pathology department's computers, allowing pathologists to view and upload data packages directly to this folder.
  - **NO-BACKUP-SPACE** - This directory is not backed up as it serves solely for the transfer of data between pathologists and the storage, acting as a location where pathologists upload input data from which the pipeline scripts retrieve and process the data automatically.
    - **Libraries**  
     Sequencing libraries uploaded by the pathology team are subsequently transferred to SensitiveCloud, where they serve as the source of library preparation metadata for the metadata catalog.
    
    - **Output**  
      This folder should be labeled as **RETRIEVED**.
    
    - **RETRIEVED**  
      This folder contains the output of the retrieval application used by pathologists to retrieve data from SensitiveCloud.
    
    - **TRANSFER**  
      This folder contains data uploaded by the pathology team. From here, the data is pseudonymized and transferred to SensitiveCloud.

- **/muni-ss** - This directory is mounted to SensitiveCloud, where we securely store sensitive data in a pseudonymized form.
  - **Libraries**  
    Sequencing libraries copied from the NO-BACKUP-SPACE folder. These libraries are used for catalog uploads, as they contain important metadata.
  
  - **Patients**  
    1. way of accessing pseudonymised integrated data package according the patients who have sequencing data and have also signed informed consent. (e.g. Patients/1990/mmci_predictive_f78e8bb9-4c2f-20f7-ab40-46aa8027c9a2) 
  
  - **OrganisedRuns**  
    2. way of accessing pseudonymised integrated data package according the sequencing run. (e.g. /muni-ss/OrganisedRuns/2023/MiSEQ/231115_M02340_0385_000000000-L8HT3/Samples/mmci_predictive_f78e8bb9-4c2f-20f7-ab40-46aa8027c9a2)
  
  - **PSEUDONYMIZED**  
    This directory contains pseudonymized files that have not yet been processed by the organization script.

- **/home/export**
  - **logs**  
    Logs from individual cron runs are stored in this folder.
  
  - **data-catalogue-pseudonymisation**  
    This is the pseudonymization repository containing the pseudonymization scripts.

- **/pseudo_tables**
  - This folder contains pseudonymization tables that serve as a backup alongside the PostgreSQL database.
