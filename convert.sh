#!/bin/sh

#--------------------------------------------------------------------------------------------------------------------#
# SCRIPT: convert.sh
#
# Author: Kevin Geoghegan
# Creation Date: 8 June 2015
# Last Updated: 8 June 2015
#
# DESCRIPTION:
# This script is a wrapper that executes outlineConvert.py followed by running sed
# commands on the resulting output file. Refer to the file outlineConvert.py for more
# information.
#
# EXTERNAL PROGRAMS USED:
# 1. outlineConvert.py
#    converts org-mode headline-based outline to TeX file using the outline package
#    format
#
# REQUIRED USER INPUT:
# Input the (i) Org-Mode file
#
# UPDATES:
#
# USAGE:
#
#--------------------------------------------------------------------------------------------------------------------#

inputFile=$1
outputFile=${inputFile//org/tex}
echo 'Input file:' ${1}

python ~/Repos/OutlineFromOrgToTeX/outlineConvert.py $1

echo 'Escaping special TeX characters...'

# TIP - regexp to find any character except x: [^x]
sed 's/&/\\&/g
s/\$/\\$/g
s/>=/$&$/g
s/\([^\$]\)>/\1$>$/g
s/<=/$&$/g
s/\([^\$]\)</\1$<$/g
s/_/\\_/g' $outputFile > text.out

cp text.out $outputFile
rm text.out

echo "Generated '"$outputFile"'\n"
latexmk -quiet $outputFile
latexmk -c

echo '\nPDF version of outline successfully generated!'
