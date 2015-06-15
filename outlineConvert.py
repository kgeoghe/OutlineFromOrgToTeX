from sys import argv
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('filename', help='type the filename on which to operate')
parser.add_argument('--margin', nargs='?', default='1',\
                    help='uniform margin width, in inches, to use in final PDF document; default is 1')
parser.add_argument('--unit', nargs='?', default='in',\
                    help='margin width units; default is in (inches)')
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
bulletIndentLevel = 0
bulletIndentation = ""

preamble = "\documentclass{report}\n\
\usepackage{outline}\n\
\usepackage[letterpaper,margin=%s%s]{geometry}\n\
\usepackage[mmddyy]{datetime}\n\
\\renewcommand{\dateseparator}{--}\n\
\usepackage{fancyhdr}\n\
\\renewcommand{\headrulewidth}{0pt}\n\
\lfoot{Rev. \\today}\n\
\cfoot{}\n\
\\rfoot{\\thepage}\n\
\pagestyle{fancy}\n\
\\begin{document}\n" % (args.margin,args.unit)

try:
    destination.write(preamble)

    for line in target:
        output = ""
        if line == '\n':  # skip empty lines
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

        # leading backslashes cause text to be flush left
        elif firstString[0] == '\\':
            if lastLineFirstChar == "":
                output = " ".join(words) + "\n"
            else: output = "\\\\" + " ".join(words) + "\n"

        # case for any text other than that beginning with a '*', '-', or '\'
        else:
            if lastLineFirstChar == "":
                output = " ".join(words) + "\n"
            else:
                output = "\\\\" + indentation + bulletIndentation + " ".join(words) + "\n"

        destination.write(output)

    # \end any hanging outline or itemize
    output = ""
    while leadingTabsOld > -1:
        bulletIndentation = "\t" * leadingTabsOld
        output += indentation + bulletIndentation + "\end{itemize}\n"
        leadingTabsOld -= 1
    while headlineIndentLast > 0:
        headlineIndentLast -= 1
        indentation = "\t" * headlineIndentLast
        output += indentation + "\end{outline}\n"

    output += "\end{document}"
    destination.write(output)

finally:
    target.close()
    destination.close()

print "Conversion to TeX syntax completed successfully."
