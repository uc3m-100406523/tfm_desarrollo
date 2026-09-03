#! /bin/bash

# Working directory
SCRIPTS_DIR="$HOME/Repositories/tfm_desarrollo/scripts"

# Look for pictures to edit
find ./comparaciones/ -type f -name *3d_hist* > $SCRIPTS_DIR/lista_editables.txt

# Edit pictures
for LINE in $(cat $SCRIPTS_DIR/lista_editables.txt)
do
    magick $LINE -crop "1460x1520+320+200" "$LINE"_cropped.png
done

# Remove pictures created by editing pictures that were already edited
find ./comparaciones/ -type f -name *_cropped.png_cropped.png -exec rm {} +
