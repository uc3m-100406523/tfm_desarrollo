#! /bin/bash

FULLPATH="$HOME/simulaciones"
DIRS1=$(ls $FULLPATH/)
for DIR1 in $DIRS1
do
    DIRS2=$(ls "$FULLPATH/$DIR1")
    for DIR2 in $DIRS2
    do
        echo "$FULLPATH/$DIR1/$DIR2"
        if ls "$FULLPATH/$DIR1/$DIR2/mac" | grep png > /dev/null
        then
            echo "POSITIVE"
        else
            echo "NEGATIVE"
        fi
    done
done
