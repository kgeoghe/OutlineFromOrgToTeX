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

python outlineConvert.py $1

echo 'Escaping special TeX characters...'

sed 's/&/\\&/g' $outputFile > text.out
# Add more replace commands for other characters that need to be excaped in LaTeX
# Example:
# sed 's/{#1}/'$timeStart'/g
# s/{#2}/'$timeEnd'/g
# s/{#3}/'$storm'\/'$domain'\/'$intensity'\/'$fValue'/g
# s/{#4}/multRun\/output/g
# s/{#5}/'$fValue'/g' templateRCL.card > multRun/rdhm$fValue.card

cp text.out $outputFile
rm text.out

echo "Generated '"$outputFile"'\n"
latexmk -c $outputFile

echo '\nPDF version of outline successfully generated!'
