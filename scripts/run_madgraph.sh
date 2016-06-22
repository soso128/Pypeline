#!/bin/bash

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
cp $TAR_DIR/$MADGRAPH.tar.gz $SCRATCH/
cd $SCRATCH
tar -xzf $SCRATCH/$MADGRAPH.tar.gz
rm $SCRATCH/$MADGRAPH.tar.gz
cd $local
cp $1/*card*.dat $SCRATCH/$MADGRAPH/
cd $SCRATCH/$MADGRAPH
./bin/mg5_aMC proc_card_mg5.dat
model=`grep ^output proc_card_mg5.dat | awk '{print $2}'`
cp run_card.dat $model
cp $2 $model/param_card.dat
cd $model/Events/
../bin/generate_events 0 run_01 > madgraph_output.txt
mv madgraph_output.txt run_01
cd run_01
# Get decay width and/or cross section
awk '{if($1 == "Width") print $3}' < madgraph_output.txt > width.txt
awk '{if($1 == "Cross-section") print $3}' < madgraph_output.txt > MG_xsec.txt
cat MG_xsec.txt
ls
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
