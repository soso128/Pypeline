#!/bin/bash

source env_file.sh

if [ -e $TAR_DIR/MadGraph5.tar.gz ]
then
    exit 0
fi

if mkdir ../misc/lock
then

    rm -r $TAR_DIR/MadGraph5/
    mkdir $TAR_DIR/MadGraph5/
    local=$PWD

    for content in $MADGRAPH/*
    do
        if [ -d $content ]
        then
            if [ ! \( -d $content/Events -a -d $content/Cards -a -d $content/SubProcesses \) ]
            then
                echo $content
                cp -r $content $TAR_DIR/MadGraph5/
            fi
        else
            echo "file       "$content
            cp $content $TAR_DIR/MadGraph5/
        fi
    done
    # If Pythia is needed, install it
    if [ $1 -eq 1 -a ! \( -d pythia-pgs \) ]
    then
        echo "install pythia-pgs" > $TAR_DIR/MadGraph5/install_pythiapgs
        cd $TAR_DIR/MadGraph5/
        ./bin/mg5 install_pythiapgs
        rm install_pythiapgs
        cd $local
    fi
    cd $TAR_DIR
    tar -czf MadGraph5.tar.gz MadGraph5
    cd $local
    echo $PWD
    rm -r ../misc/lock
fi
