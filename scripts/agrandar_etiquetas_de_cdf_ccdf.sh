#! /bin/bash

# Working directory
SCRIPTS_DIR="$HOME/Repositories/tfm_desarrollo/scripts"

# Look for pictures to edit
find ./computos_y_graficas/ -type f -name cdf_ildl.png > $SCRIPTS_DIR/lista_editables.txt

# Edit pictures
for LINE in $(cat $SCRIPTS_DIR/lista_editables.txt)
do
    magick $SCRIPTS_DIR/../images/cdf_ildl_marco.png $LINE -gravity Center -region 720x535+27+0 -composite "$LINE"_fixed.png
done

# Look for pictures to edit
find ./computos_y_graficas/ -type f -name ccdf_ildl.png > $SCRIPTS_DIR/lista_editables.txt

# Edit pictures
for LINE in $(cat $SCRIPTS_DIR/lista_editables.txt)
do
    magick $SCRIPTS_DIR/../images/ccdf_ildl_marco.png $LINE -gravity Center -region 720x535+27+0 -composite "$LINE"_fixed.png
done

# Remove pictures created by editing pictures that were already edited
find ./computos_y_graficas/ -type f -name *_fixed.png_fixed.png -exec rm {} +
