#!/bin/bash

# Source the environment variables
source env_file.sh

local=$PWD
script_name="null"
output_dir="null"
output_files="null"
# Parse optional command line arguments
# -l if the run is local (expect SCRATCH name)
# -s if there is a custom script to run (script name)
# -o if we expect output (output_dir)
# -f listing files to be outputted
while getopts l:s:o:f: opt
do
    case $opt in
        l) SCRATCH="$OPTARG"
        ;;
        s) script_name="$OPTARG"
        ;;
        o) output_dir="$OPTARG"
        ;;
        f) output_files="$OPTARG"
        ;;
        \?) echo "Invalid option -$OPTARG" >&2
        ;;
    esac
done
# Get job directory (cards) and param card name
jobdir=${@:$OPTIND:1}
parname=${@:$OPTIND+1:1}
# Install MadGraph locally
cp $TAR_DIR/$MADGRAPH.tar.gz $SCRATCH/
cd $SCRATCH
tar -xzf $SCRATCH/$MADGRAPH.tar.gz
rm $SCRATCH/$MADGRAPH.tar.gz
cd $local
# Get Cards
cp $jobdir/*card*.dat $SCRATCH/$MADGRAPH/
cd $SCRATCH/$MADGRAPH
# Generate output for the process and grab model name
./bin/mg5_aMC proc_card_mg5.dat
model=`grep ^output proc_card_mg5.dat | awk '{print $2}'`
rm proc_card_mg5.dat
# Copy other cards in the model/Cards directory
cp *card* $model/Cards/
cp $model/Cards/$parname $model/Cards/param_card.dat
cd $model/Events/
# Edit the me5_configuration file to add Pythia and Delphes directories
# if necessary
if [ -f ../Cards/pythia_card.dat ]
then
    echo "pythia-pgs_path="$PYTHIAPGS >> ../Cards/me5_configuration.txt
fi
if [ -f ../Cards/delphes_card.dat ]
then
    echo "delphes_path="$DELPHES >> ../Cards/me5_configuration.txt
fi
# Run MadGraph (+ Pythia + Delphes if the cards are there)
../bin/generate_events 0 run_01 #> madgraph_output.txt
mv madgraph_output.txt run_01
cd run_01
# Get decay width and/or cross section
awk '{if($1 == "Width") print $3}' < madgraph_output.txt > width.txt
awk '{if($1 == "Cross-section") print $3}' < madgraph_output.txt > MG_xsec.txt
# If asked, run custom script
if [ $script_name != "null" ]
then
    cp $scriptname .
    ./$scriptname madgraph_output.txt
fi
# If output, copy files over
if [ $output_dir != "null" ]
then
    for file in $output_files
    do
        cp $file $output_dir/
    done
fi
cd $local
rm -r $SCRATCH
