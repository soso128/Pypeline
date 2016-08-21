#!/bin/bash

source env_file.sh

if [ $# -lt 1 ]
then
    echo "Usage: ./launch.sh <input card> [<truncate>]"
    exit 1
fi

card=$1

truncate=0
if [ $# -gt 1 ]
then
    truncate=$2
fi

$PYTHON3 -c "import run_madgraph as rp; rp.script_from_yaml('$card', truncate = $truncate)"
