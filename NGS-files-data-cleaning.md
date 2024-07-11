Within the process of data cleaning, the following files are stored for future use.

| **SEQUENCING MACHINE OUTPUT**                      | **NextSeq**                                      | **MiSeq**                                           |
|----------------------------------------------------|--------------------------------------------------|-----------------------------------------------------|
|                                                    | SampleSheet.csv                                  | SampleSheet.csv                                     |
|                                                    | RunParameters.xml                                | RunParameters.xml                                   |
|                                                    | RunInfo.xml                                      | RunInfo.xml                                         |
|                                                    | RunCompletionStatus.xml                          | CompletedJobInfo.xml                                |
|                                                    | Data/Intensities/BaseCalls/L001(.bcl.bgzf files) | GenerateFASTQRunStatistics.xml                      |
|                                                    |                                                  | Data/Intensities/BaseCalls/[predictive_number].fastq.gz |
|                                                    |                                                  | Data/Intensities/BaseCalls/Alignment/               | 
|                                                    |                                                  |    • AdapterCounts.txt                              |
|                                                    |                                                  |    • AdapterTrimming.txt                            |
|                                                    |                                                  |    • DemultiplexSummaryF1L1.txt                     |
|                                                    |                                                  |    • Checkpoint.txt                                 |
| **ANALYSIS OUTPUT**                                | **Clinical Genomics Workspace (CGW)**            | **NextGENe**                                        |
|                                                    |• [predictive_number]_DNA.bam                     | [predictive_number] folder                          |
|                                                    |• [predictive_number]_DNA.bam.bai                 | • [predictive_number].bam                           |
|                                                    |• Main.vcf                                        | • [predictive_number].bam.bai                       |
|                                                    |• DNA_Sequencing_QC_Metrics_Report_               | • bamconversion.txt                                 |
|                                                    |                                                  | • [predictive_number]_Parameters.txt                |
|                                                    |                                                  | • [predictive_number]_StatInfo.txt                  |
|                                                    |                                                  | • whole folder Reports (containing VCF files)       |
|                                                    |                                                  | preprocessed folder                                 |
|                                                    |                                                  | • Unique_convert.txt per R1/_convert.txt per R1     |
|                                                    |                                                  | • Unique_converted.fasta per R1/_converted.fasta per R1|
|                                                    |                                                  | • Unique_convert.txt per R2/_convert.txt per R2 
|                                                    |                                                  | • Unique_converted.fasta per R2/_converted.fasta per R2|
|                                                    |                                                  | • in case of availability: RemoveDuplicates.txt     | 


