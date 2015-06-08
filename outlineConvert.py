from sys import argv

script, filename = argv

basename = filename[:-4]
to_filename = basename + ".tex"

destination = open(to_filename, 'w')

print "Opening the file..."
target = open(filename)

headlineIndentLast = 0
indentLevel = 0

preamble = "\documentclass{report}\n\
\usepackage{outline}\n\
\usepackage[letterpaper,margin=1in]{geometry}\n\
\usepackage{fancyhdr}\n\
\\renewcommand{\headrulewidth}{0pt}\n\
\cfoot{}\n\
\\rfoot{\\thepage}\n\
\pagestyle{fancy}\n\
\\begin{document}\n"

destination.write(preamble)

for line in target:
    words = line.split()
    firstString = words[0]
    
    if firstString[0] == '*':
        headlineIndent = len(firstString)
        indentation = "\t" * indentLevel
        if headlineIndent > headlineIndentLast:
            output = indentation + "\\begin{outline}\n" + indentation + "\t\item " +\
                     " ".join(words[1:]) + "\n"
            indentLevel += 1
        elif headlineIndent == headlineIndentLast:
            output = indentation + "\item " + " ".join(words[1:]) + "\n"
        else:
            indentDiff = headlineIndentLast - headlineIndent
            output = ""
            while indentDiff / 2 != 0: # int division by two--only use odd number of asterisks in
                # org-mode headlines
                indentLevel -= 1
                indentation = "\t" * indentLevel
                output += indentation + "\end{outline}\n"
                indentDiff -= 2
            output += indentation + "\item " + " ".join(words[1:]) + "\n"
    else:
        output = indentation + "\\ " + " ".join(words) + "\n"
            
    destination.write(output)
    headlineIndentLast = headlineIndent

destination.write("\end{outline}\n\end{document}")

target.close()
destination.close()
