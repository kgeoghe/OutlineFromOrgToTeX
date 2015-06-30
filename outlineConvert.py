from sys import argv
import re
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('filename',\
                    help='type the filename on which to operate')
parser.add_argument('-d', '--draft', action='store_true',\
                    help='produce roomy draft instead of tightly spaced document')
parser.add_argument('-b', '--bib', action='store_true',\
                    help='includes citations')
parser.add_argument('-m', '--margin', nargs='?', default='1',\
                    help='uniform margin width to use in final PDF document; default is 1')
parser.add_argument('-u', '--unit', nargs='?', default='in',\
                    help='margin width units; default is in (inches)')
parser.add_argument('-n', '--nonuniform', action='store_true',\
                    help='specify individual (nonuniform) margin widths')
parser.add_argument('-1', '--lmargin', nargs='?', default='1.5',\
                    help="left margin, if using '-n' flag; default is 1.5")
parser.add_argument('-2', '--tmargin', nargs='?', default='1',\
                    help="top margin, if using '-n' flag; default is 1")
parser.add_argument('-3', '--rmargin', nargs='?', default='1.5',\
                    help="right margin, if using '-n' flag; default is 1.5")
parser.add_argument('-4', '--bmargin', nargs='?', default='1',\
                    help="bottom margin, if using '-n' flag; default is 1")
args = parser.parse_args()

basename = args.filename[:-4]
to_filename = basename + ".tex"

destination = open(to_filename, 'w')

print "Opening the file..."
print "Using %s %s margins..." % (args.margin,args.unit)
target = open(args.filename)


### For Testing ####
# try:
#     # for line in target:
#     #     print line
#     for line in target.readlines()[2:]:
#         print line
#     print 'Contents of file %r' % filename + ' are printed above.'
# finally:
#     target.close()
# quit()
################

indentation = ""
headlineIndentLast = 0
indentLevel = 0
leadingTabsOld = 0
lastLineFirstChar = ""
lastLineFirstTwoChars = ""
bulletIndentLevel = 0
leadingTabsOld = -1
bulletIndentation = ""
continueEnumerate = ""

footSkip = ""
if float(args.margin) <= 0.75:
    footSkip = ",footskip=12pt"
addToPreamble = ""
linespace = ""
geometry = "\usepackage[letterpaper,margin=%s%s%s,hmarginratio=1:1]{geometry}" % (args.margin,args.unit,footSkip)
if args.nonuniform==True:
        geometry = "\usepackage[letterpaper,left=%s%s,top=%s%s,right=%s%s,bottom=%s%s%s,asymmetric]{geometry}" % (args.lmargin,args.unit,args.tmargin,args.unit,args.rmargin,args.unit,args.bmargin,args.unit,footSkip)
if args.draft==True:
    addToPreamble += "\setlist[itemize]{noitemsep, topsep=0pt}\n\setlist[enumerate]{noitemsep, topsep=0pt}\n\def\\textvcenter\n\t{\hbox \\bgroup$\everyvbox{\everyvbox{}%\n\t\\aftergroup$\\aftergroup\egroup}\\vcenter}\n"
    linespace = "\doublespacing\n"
preamble = "\documentclass[twoside]{report}\n\
\usepackage{outline}\n\
%s\n\
\usepackage[mmddyy]{datetime}\n\
\usepackage{setspace}\n\
\usepackage{enumitem}\n\
\\renewcommand{\dateseparator}{--}\n\
\usepackage{natbib}\n\
\usepackage{fancyhdr}\n\
\\renewcommand{\headrulewidth}{0pt}\n\
\\fancyfoot{}\n\
\\fancyfoot[LO,RE]{Rev. \\today}\n\
\\fancyfoot[LE,RO]{\\thepage}\n\
\pagestyle{fancy}\n%s\
\\begin{document}\n\
\\noindent\n\
%s" % (geometry,addToPreamble,linespace)

bibData = ""
if args.bib==True:
    bibData = "\\renewcommand{\\bibname}{References}\n\
\\bibliographystyle{plainnatmod}   %this references the modified .bst file in the local directory \n\
\singlespace\n\
\\bibliography{/Users/kgeoghe/Dropbox/article-store/_article_store}\n"

try:
    destination.write(preamble)

    for line in target:
        output = ""
        if line == '\n':                                      # skip empty lines
            if lastLineFirstChar == "":           # purely skip lines in file header
                continue
            else:                                              # retain line skips I have in source file
                while leadingTabsOld > -1:   # escape out of all outline/itemize envs. if linebreak
                    bulletIndentation = "\t" * leadingTabsOld
                    output += indentation + bulletIndentation + "\end{itemize}\n"
                    leadingTabsOld -= 1
                while headlineIndentLast > 0:
                    headlineIndentLast -= 1
                    indentation = "\t" * headlineIndentLast
                    output += indentation + "\end{outline}\n"

                if lastLineFirstTwoChars == "TK":  # check to see if need to close "TK" enumerate
                    output += "\end{enumerate}\n"
                output += "\\vspace{1em}\n"
                destination.write(output)
                lastLineFirstChar = "\n"
                lastLineFirstTwoChars = "\n"
                continue

        words = line.split()
        firstString = words[0]

        # skip org file-specific settings
        if firstString[0:3] == '-*-' or firstString[0:2] == '#+':
            continue

        # case for org headlines (asterisks) lines
        elif firstString[0] == '*':
            headlineIndent = len(firstString)

            # first, take care of end itemize if last line started with a "-"
            if lastLineFirstChar == "-":
                while leadingTabsOld > -1:
                    bulletIndentation = "\t" * leadingTabsOld
                    output += indentation + bulletIndentation + "\end{itemize}\n"
                    leadingTabsOld -= 1

            # moving deeper into outline
            if headlineIndent > headlineIndentLast:
                output += indentation + "\\begin{outline}\n" + indentation + "\t\item " +\
                         " ".join(words[1:]) + "\n"
                indentLevel += 1
            # staying at same level in outline
            elif headlineIndent == headlineIndentLast:
                output += indentation + "\item " + " ".join(words[1:]) + "\n"
            # moving to higher outline levels
            else:
                indentDiff = headlineIndentLast - headlineIndent
                while indentDiff / 2 > 0: # int division by two--only use odd number of asterisks in
                    # org-mode headlines
                    indentLevel -= 1
                    indentation = "\t" * indentLevel
                    output += indentation + "\end{outline}\n"
                    indentDiff -= 2
                output += indentation + "\item " + " ".join(words[1:]) + "\n"

            indentation = "\t" * indentLevel
            bulletIndentLevel = 0  # not in bullet list, so reset bullet indent. level
            lastLineFirstChar = firstString[0]
            headlineIndentLast = headlineIndent

        # case for bulleted lists lines
        elif firstString[0] == '-':
            leadingSpaces = len(line) - len(line.lstrip(' '))  # leading spaces in org file line
            leadingTabs = (leadingSpaces / 2)                   # convert spaces into num. of  tabs
            bulletIndentation = "\t" * bulletIndentLevel

            if lastLineFirstChar == '*' or leadingTabs > leadingTabsOld or lastLineFirstChar == "":
                output = indentation + bulletIndentation + "\\begin{itemize}\n" + indentation +\
                         bulletIndentation + "\t\item " + " ".join(words[1:]) + "\n"
                bulletIndentLevel += 1
            elif leadingTabs == leadingTabsOld:
                output = indentation + bulletIndentation + "\item " + " ".join(words[1:]) + "\n"
            else:
                bulletIndentDiff = leadingTabsOld - leadingTabs
                while bulletIndentDiff > 0:
                    bulletIndentLevel -= 1
                    bulletIndentation = "\t" * bulletIndentLevel
                    output += indentation + bulletIndentation + "\end{itemize}\n"
                    bulletIndentDiff -= 1
                output += indentation + bulletIndentation + "\item " + " ".join(words[1:]) + "\n"

            leadingTabsOld = leadingTabs
            lastLineFirstChar = firstString[0]

        # case for "TK"s
        elif re.match('TK',firstString):
            if lastLineFirstTwoChars != 'TK':
                output = "\\begin{enumerate}%s\n" % continueEnumerate +\
                         "\t\item[\\textvcenter{\hbox{\\tiny{%s}}}]{\small " % firstString +\
                         " ".join(words[1:]) + "}\n"
            else:
                output = "\t\item[\\textvcenter{\hbox{\\tiny{%s}}}]{\small " % firstString +\
                         " ".join(words[1:]) + "}\n"
            continueEnumerate = "[resume]"
            
        # leading backslashes cause text to be flush left
        elif firstString[0] == '\\':
            if lastLineFirstTwoChars == "TK":  # check to see if need to close "TK" enumerate
                output += "\end{enumerate}\n"
            if lastLineFirstChar == "":
                output += " ".join(words) + "\n"
            else:
                output += "\\\\" + " ".join(words) + "\n"

        # case for any text other than that beginning with a '*', '-', or '\'
        else:
            if lastLineFirstTwoChars == "TK":  # check to see if need to close "TK" enumerate
                output += "\end{enumerate}\n"
            if lastLineFirstChar == "":
                output += " ".join(words) + "\n"
            else:
                output += "\\\\" + indentation + bulletIndentation + " ".join(words) + "\n"

        lastLineFirstChar = firstString[0]
        lastLineFirstTwoChars = firstString[0:2]
        destination.write(output)

    # \end any hanging outline or itemize
    output = ""
    if lastLineFirstTwoChars == "TK":
        output += "\end{enumerate}\n"
    while leadingTabsOld > -1:
        bulletIndentation = "\t" * leadingTabsOld
        output += indentation + bulletIndentation + "\end{itemize}\n"
        leadingTabsOld -= 1
    while headlineIndentLast > 0:
        headlineIndentLast -= 1
        indentation = "\t" * headlineIndentLast
        output += indentation + "\end{outline}\n"

    output += bibData + "\end{document}"
    destination.write(output)

finally:
    target.close()
    destination.close()

print "Conversion from Org Mode to TeX syntax completed successfully."
