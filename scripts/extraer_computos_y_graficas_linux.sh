#! /bin/bash

rsync --recursive --delete --times --progress --exclude=*log* "<ruta al directorio con las simulaciones>" "<ruta al directorio donde guardar los cómputos y las gráficas>"
