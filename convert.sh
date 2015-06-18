#!/bin/sh

#--------------------------------------------------------------------------------------------------------------------#
# SCRIPT: convert.sh
#
# Author: Kevin Geoghegan
# Creation Date: 8 June 2015
# Last Updated: 15 June 2015
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

while getopts ":m:u:hd" opt; do
    case $opt in
        d)
            draft="--draft $OPTARG" >&2
            ;;
        m)
            margin="--margin $OPTARG" >&2
            ;;
        u)
            unit="--unit $OPTARG" >&2
            ;;
        h)
            python ~/Repos/OutlineFromOrgToTeX/outlineConvert.py -h
            exit 1
            ;;
        \?)
            echo "Invalid option: -$OPTARG" >&2
            exit 1
            ;;
        :)
            echo "Option -$OPTARG requires an argument." >&2
            exit 1
            ;;
    esac
done

shift $(( OPTIND-1 ))

inputFile=$1
outputFile=${inputFile//org/tex}
pdfFile=${inputFile//org/pdf}
echo "Running command 'python ~/Repos/OutlineFromOrgToTeX/outlineConvert.py" ${draft} ${margin} ${unit} ${1}"'"
#echo 'Input file:' ${1}

python ~/Repos/OutlineFromOrgToTeX/outlineConvert.py $draft $margin $unit $1

echo 'Escaping special TeX characters...'

# TIP - regexp to find any character except x: [^x]
sed 's/&/\\&/g
s/\$/\\$/g
s/>=/$&$/g
s/\([^\$]\)>/\1$>$/g
s/<=/$&$/g
s/\([^\$]\)</\1$<$/g
s/_/\\_/g
s/\([^\\textsuperscript{]\)TK\([0-9]*\)/\1\\textsuperscript{TK\2}/g' $outputFile > text.out

cp text.out $outputFile
rm text.out

echo "Generated '"$outputFile"'\n"
latexmk -quiet $outputFile
latexmk -c

echo "\n'"$pdfFile"' successfully generated!"
