!/bin/bash

source env_file.sh

local=$PWD
cp $TAR_DIR/$MADGRAPH.tar.gz $SCRATCH/
tar -xzf $SCRATCH/$MADGRAPH.tar.gz
rm $SCRATCH/$MADGRAPH.tar.gz
cp $1/*card*.dat $SCRATCH/$MADGRAPH/
cd $SCRATCH/$MADGRAPH
./bin/mg5_aMC proc_card_mg5.dat
model=`grep ^output proc_card_mg5.dat | awk '{print $2}'`
cp run_card.dat $model
cp param_card_$2.dat $model/param_card.dat
cd $model/Events/
../bin/generate_events 0 run_01
cd $local
rm -r $SCRATCH
