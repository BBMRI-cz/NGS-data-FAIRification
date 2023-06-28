import molgenis.client

session = molgenis.client.Session("https://data.bbmri.cz")
session.login("*********", "*******")

session.add('fair-genomes_personal',
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


#session.add('fair-genomes_clinical')

session.add("fair-genomes_sequencing",
            sequencingidentifier="0043/9",
            sequencingplatform="Illumina platform",
            sequencinginstrumentmodel= "MiSeq",
            sequencingmethod= "Sequencing by Synthesis",
            averagereaddepth= "",
            observedreadlength="101",
            observedinsertsize= "",
            otherqualitymetrics= "Cluster Density 149.921371; Clusters Passing Filter 92.21017; Estimated Yield \n76.7622452; Error Description NA; Num Lanes 4; Flowcell ID HC2G2BGXH\n")

session.add("fair-genomes_samplepreparation",
            sampleprepidentifier= "sampleprep_A2020/15",
            belongstomaterial= "mmci_XXXXXXXXXXXX",
            inputamount= "15",
            librarypreparationkit="Accel\u2122  Amplicon  Custom Core  Kit ",
            pcrfree="false",
            targetenrichmentkit= "Accel\u2122  Amplicon  Custom Core  Kit",
            umispresent= "false",
            intendedinsertsize= "265",
            intendedreadlength= "282")

session.add("")




session.logout()
