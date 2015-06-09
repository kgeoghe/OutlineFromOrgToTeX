from sys import argv

script, filename = argv

basename = filename[:-4]
to_filename = basename + ".tex"

destination = open(to_filename, 'w')

print "Opening the file..."
target = open(filename)


### For Testing ####
# try:
#     for line in target:
#         print line
#     print 'Contents of file %r' % filename + ' are printed above.'
# finally:
#     target.close()
# quit()
################

headlineIndentLast = 0
indentLevel = 0
leadingTabsOld = 0
lastLineFirstChar = ""
bulletIndentLevel = 0

preamble = "\documentclass{report}\n\
\usepackage{outline}\n\
\usepackage[letterpaper,margin=1in]{geometry}\n\
\usepackage{fancyhdr}\n\
\\renewcommand{\headrulewidth}{0pt}\n\
\cfoot{}\n\
\\rfoot{\\thepage}\n\
\pagestyle{fancy}\n\
\\begin{document}\n"

try:
    destination.write(preamble)

    for line in target:
        output = ""
        words = line.split()
        firstString = words[0]

        # case for org headlines (asterisks) lines
        if firstString[0] == '*':
            headlineIndent = len(firstString)
            indentation = "\t" * indentLevel

            # first, take care of end itemize if last line started with a "-"
            if lastLineFirstChar == "-":
                while leadingTabsOld > -1:
                    bulletIndentation = "\t" * leadingTabsOld
                    output += indentation + bulletIndentation + "\end{itemize}\n"
                    leadingTabsOld -= 1

            if headlineIndent > headlineIndentLast:
                output += indentation + "\\begin{outline}\n" + indentation + "\t\item " +\
                         " ".join(words[1:]) + "\n"
                indentLevel += 1
            elif headlineIndent == headlineIndentLast:
                output += indentation + "\item " + " ".join(words[1:]) + "\n"
            else:
                indentDiff = headlineIndentLast - headlineIndent
                while indentDiff / 2 > 0: # int division by two--only use odd number of asterisks in
                    # org-mode headlines
                    indentLevel -= 1
                    indentation = "\t" * indentLevel
                    output += indentation + "\end{outline}\n"
                    indentDiff -= 2
                output += indentation + "\item " + " ".join(words[1:]) + "\n"

            bulletIndentLevel = 0  # not in bullet list, so reset bullet indent. level
            lastLineFirstChar = firstString[0]
            headlineIndentLast = headlineIndent

        # case for bulleted lists lines
        elif firstString[0] == '-':
            leadingSpaces = len(line) - len(line.lstrip(' '))  # leading spaces in org file line
            leadingTabs = (leadingSpaces / 2)                   # convert spaces into num. of  tabs
            bulletIndentation = "\t" * bulletIndentLevel
            
            if lastLineFirstChar == '*' or leadingTabs > leadingTabsOld:
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

        # case for any text other than that beginning with a '*' or '-'
        else:
            output = "\\\\" + indentation + bulletIndentation + " ".join(words) + "\n"
            
        destination.write(output)
    
    destination.write("\end{outline}\n\end{document}")

finally:
    target.close()
    destination.close()

print "Conversion completed successfully."
