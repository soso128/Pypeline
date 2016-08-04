#!/bin/bash

source env_file.sh

card=$1

truncate=0
if [ $# -gt 1 ]
then
    truncate=$2
fi

$PYTHON3 -c "import run_madgraph as rp; rp.script_from_yaml('$card', truncate = $truncate)"
