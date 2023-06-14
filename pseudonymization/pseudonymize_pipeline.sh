FILES="../playground/seq/TRANSFER" #$1
FULL_EXPORT="patient_exports/"
PREDICTIVE_EXPORT="../playground/patient_predictive" #$2
PSEUDO_TABLE="../playground/pseudonimisation_table/pseudo_table.json" #$3
BH_SERVER_TRANSFER="sequencing@bridgehead01.int.mou.cz:/home/mou/patient_data/"
SC_FOLDER="../playground/muni-sc"


#pull image
rsync -vdru --min-size=350 $BH_SERVER $FULL_EXPORT
#filter
grep -lEir $FULL_EXPORT -e 'predictive_number="[0-9]{4}/[0-9]{1,4}"' | xargs cp -t $PREDICTIVE_EXPORT
#remove duplicates
fdupes -dN $PREDICTIVE_EXPORT

for f in "${FILES}/*"; do
    echo $f
    bash remove_files.sh $f
    python pseudonymization.py -r $f -e $PREDICTIVE_EXPORT -p $PSEUDO_TABLE
    bash replace_predictive.sh "${PSEUDO_TABLE}.temp" $f
    rm "${PSEUDO_TABLE}.temp"
    mv $f "${SC_FOLDER}/."
done