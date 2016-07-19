#!/bin/bash

# Source the environment variables
source env_file.sh

local=$PWD
script_name="null"
output_dir="null"
output_files="null"
grid_status="null"
grid_dir="null"
# Parse optional command line arguments
# -l if the run is local (expect SCRATCH name)
# -s if there is a custom script to run (script name)
# -o if we expect output (output_dir)
# -f listing files to be outputted
# -g gridpack status if needed
# -h gridpack directory if needed
# -j job directory
# -p file names with parameters
while getopts l:s:o:f:g:h:j:p: opt
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
        g) grid_status="$OPTARG"
        ;;
        h) grid_dir="$OPTARG"
        ;;
        j) jobdir="$OPTARG"
        ;;
        p) parname="$OPTARG"
        ;;
        \?) echo "Invalid option -$OPTARG" >&2
        ;;
    esac
done
# Starting from an existing gridpack
if [ $grid_status == 1 ]
then
    cd $SCRATCH/
    mkdir Template
    cd Template
    mkdir Cards Events
    cp $local/$jobdir/*card*.dat Cards/
    cd Events/
    cp $grid_dir/gridpack_$parname.tar.gz .
    tar --force-local -xzf gridpack_$parname.tar.gz
    nevents=`awk '{if($3 == "nevents") print $1}' < ../Cards/run_card.dat`
    ./run.sh $nevents 0 > madgraph_output.txt
    mv events.lhe.gz unweighted_events.lhe.gz
    if [ -f ../Cards/pythia_card.dat ]
    then
        gunzip unweighted_events.lhe.gz
        ./madevent/bin/internal/run_pythia $PYTHIAPGS/src/ 
        if [ -f ../Cards/delphes_card.dat ]
        then
            ./madevent/bin/internal/run_delphes $DELPHES/
        fi
    fi
    gzip unweighted_events.lhe
    mkdir run_01
    mv * run_01/
    cd run_01
else
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
    cp $model/Cards/param_card_$parname.dat $model/Cards/param_card.dat
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
    ../bin/generate_events 0 run_01 > madgraph_output.txt
    mv madgraph_output.txt run_01
    cd run_01
    # If gridpack, move it to the desired folder
    if [ $grid_status == 0 ]
    then
        cp ../../run_01_gridpack.tar.gz $grid_dir/gridpack_$parname.tar.gz
    fi
fi
# Get decay width and/or cross section
awk '{if($1 == "Width") print $3}' < madgraph_output.txt > width.txt
awk '{if($1 == "Cross-section") print $3}' < madgraph_output.txt > MG_xsec.txt
# Display output for debugging
cat madgraph_output.txt
# If asked, run custom script
if [ $script_name != "null" ]
then
    cp $script_name .
    executable=`basename $script_name`
    chmod +x $executable
    ./$executable $parname madgraph_output.txt
fi
# Give unique names to files
mv width.txt width_$parname.txt
mv MG_xsec.txt MG_xsec_$parname.txt
for f in *.lhe.gz
do
    name=`basename $f .lhe.gz`
    mv $f $name\_$parname.lhe.gz
done
for f in *.hep.gz
do
    name=`basename $f .hep.gz`
    mv $f $name\_$parname.hep.gz
done
for f in *.root
do
    name=`basename $f .root`
    mv $f $name\_$parname.root
done
# If output, copy requested files over
if [ $output_dir != "null" ]
then
    for file in $output_files
    do
        cp $file $output_dir/
    done
fi
cd $local
rm -r $SCRATCH
