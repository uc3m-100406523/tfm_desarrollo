#! /bin/bash

DOC_NAME="5g-network-emulator-doc.md"
PDF_NAME="5g-network-emulator-doc.pdf"
HTML_NAME="5g-network-emulator-doc.htm"

touch $DOC_NAME

echo >> $DOC_NAME
echo "---" >> $DOC_NAME
echo "# FikoRE: 5g-network-emulator" >> $DOC_NAME
echo "---" >> $DOC_NAME

echo >> $DOC_NAME
cat ./index/index_alt.md >> $DOC_NAME

echo >> $DOC_NAME
cat ./5g-network-emulator/README2.md >> $DOC_NAME

echo >> $DOC_NAME
echo "## Architecture and Implementation Details" >> $DOC_NAME
cat ./5g-network-emulator.wiki/Architecture-and-Implementation.md >> $DOC_NAME

echo >> $DOC_NAME
echo "### Configuration File" >> $DOC_NAME
cat ./5g-network-emulator.wiki/Configuration-File.md >> $DOC_NAME

echo >> $DOC_NAME
echo "### Real-Time Emulation" >> $DOC_NAME
cat ./5g-network-emulator.wiki/Real-Time-Emulation.md >> $DOC_NAME

echo >> $DOC_NAME
echo "### MAC Layer" >> $DOC_NAME
cat ./5g-network-emulator.wiki/MAC-Layer.md >> $DOC_NAME

echo >> $DOC_NAME
echo "### User Equipment (UE)" >> $DOC_NAME
cat ./5g-network-emulator.wiki/User-Equipment.md >> $DOC_NAME

echo >> $DOC_NAME
echo "#### Traffic Generator" >> $DOC_NAME
cat ./5g-network-emulator.wiki/Traffic-Generator.md >> $DOC_NAME

echo >> $DOC_NAME
echo "#### Netfilter Module" >> $DOC_NAME
cat ./5g-network-emulator.wiki/Netfilter-Module.md >> $DOC_NAME

echo >> $DOC_NAME
echo "#### Mobility Models" >> $DOC_NAME
cat ./5g-network-emulator.wiki/Mobility-Models.md >> $DOC_NAME

echo >> $DOC_NAME
echo "#### Metric Estimation" >> $DOC_NAME
cat ./5g-network-emulator.wiki/Metric-Estimation.md >> $DOC_NAME

echo >> $DOC_NAME
echo "#### RLC/PDCP Layer" >> $DOC_NAME
cat ./5g-network-emulator.wiki/RLC-and-PDCP-Layer.md >> $DOC_NAME

echo >> $DOC_NAME
echo "#### PHY Layer" >> $DOC_NAME
cat ./5g-network-emulator.wiki/PHY-Layer.md >> $DOC_NAME

echo >> $DOC_NAME
echo "### Data Logging" >> $DOC_NAME
cat ./5g-network-emulator.wiki/Data-Logging.md >> $DOC_NAME

echo >> $DOC_NAME
echo "### Overall Flow" >> $DOC_NAME
cat ./5g-network-emulator.wiki/Overall-Flow.md >> $DOC_NAME

echo >> $DOC_NAME
echo "## Compilation and Usage" >> $DOC_NAME
cat ./5g-network-emulator.wiki/Compilation-and-Usage.md >> $DOC_NAME

echo >> $DOC_NAME
echo "## Annex" >> $DOC_NAME

echo >> $DOC_NAME
echo "### XR Offloading Testing" >> $DOC_NAME
cat ./5g-network-emulator.wiki/XR-Offloading-Testing.md >> $DOC_NAME

# pandoc --from markdown --to pdf --output $PDF_NAME $DOC_NAME
pandoc --from markdown --to html --output $HTML_NAME $DOC_NAME
