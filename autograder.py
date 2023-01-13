import io, sys, os, shutil, subprocess, copy, re

die = False

def printerr(*args):
    print(*args, file=sys.stderr)

# Check if Lean is installed.
if shutil.which("lean") == None:
    printerr("Lean is not installed, or not in your PATH!")
    die = True

if len(sys.argv) < 3:
    printerr("Missing arguments!")
    printerr("usage: python3 auto.py directory/containing/submissions homework/template.lean")
    exit(1)

submissionpath = sys.argv[1]
templatepath = sys.argv[2]

# Check if the directories and files are usable.
if not os.path.exists(submissionpath):
    printerr(submissionpath, "does not exist")
    die = True
elif not os.path.isdir(submissionpath):
    printerr(submissionpath, "is not a directory")
    die = True
elif not os.access(submissionpath, os.R_OK):
    printerr(submissionpath, ": Access denied")
    die = True
if not os.path.exists(templatepath):
    printerr(templatepath, "does not exist")
    die = True
elif not os.path.isfile(templatepath):
    print(templatepath, "is not a file")
    die = True
elif not os.access(templatepath, os.R_OK):
    print(templatepath, ": Access denied")
    die = True
if die == True:
    printerr("usage: python3 auto.py directory/containing/submissions homework/template.lean")
    exit(1)

try:
    sorries = str(subprocess.check_output(["lean", templatepath]))
except subprocess.CalledProcessError as e:
    sorries = str(e.output)

exampleLNs = []

sorries = sorries.replace(r'\n', '\n')
sorries = sorries.replace("\"", "")
with io.StringIO(sorries[1:]) as f:
    Warns = f.readlines()
    for i in Warns:
        if "uses sorry" in i:
            dex1 = i.index(".lean:") + 6
            s = i[dex1:]
            dex2 = s.index(":")
            exampleLNs = exampleLNs + [int(s[:dex2])]

examples = []
numExamples = 0

with open(templatepath, 'r') as f:
    lines = f.readlines()
    for i in exampleLNs:
        currEx = lines[i - 1].strip()
        if "OPTIONAL" in currEx:
            examples = examples + [[re.sub("--.*", "", currEx).strip(), True, False]]
        else:
            examples = examples + [[re.sub("--.*", "", currEx).strip(), False, False]]
            numExamples += 1

    # print("Grading:")
    # for i in examples:
    #     print(i)

# Make folders separating perfect and imperfect submissions
try: 
    os.mkdir(os.path.join(submissionpath, "Perfect"))
except OSError as e:
    pass

try: 
    os.mkdir(os.path.join(submissionpath, "For Review"))
except OSError as e:
    pass


tempFile = "autograder_temp_"
tempFileNo = 0
while os.path.exists(os.path.join(submissionpath, tempFile + str(tempFileNo) + ".lean")):
    tempFileNo += 1
tempFile = tempFile + str(tempFileNo) + ".lean"


for filename in os.listdir(submissionpath):
    for entry in examples:
        entry[2] = False
    ffilename = os.path.join(submissionpath, filename)
    if filename != tempFile and os.path.isfile(ffilename):
        if os.path.splitext(filename)[1] == ".lean":
            print(filename)
            perfect = True
            fexamples = []
            with open(ffilename, 'r') as f:
                s = f.read()
                s = re.sub("(/-.*-/)|(--.*\n)", "", s)
                i = 1
                for line in s.splitlines():
                    if "example" in line or "theorem" in line:
                        j = 0
                        for e in examples:
                            if examples[j][2] == True:
                                j += 1
                                continue
                            if e[0] in line:
                                fexamples = fexamples + [[i, j, True]]
                                examples[j][2] = True
                                break
                            j += 1
                    i += 1
                 
                for entry in examples:
                    if entry[2] == False and entry[1] == False:
                        perfect = False
                        # print("\tMissing:", entry[0])
                        break
                if not perfect:
                    os.replace(ffilename, os.path.join(submissionpath, "For Review", filename))
                    print("\tNeeds review: missing theorems!")
                    continue

                with open(os.path.join(submissionpath, tempFile), "w") as fw:
                    fw.write(s)
                fexamples.sort()
                try:
                    fsorries = str(subprocess.check_output(["lean", os.path.join(submissionpath , tempFile)]))
                except subprocess.CalledProcessError as e:
                    fsorries = str(e.output)

                # print(fsorries)

                fsorries = fsorries.replace(r'\n', '\n')
                # for entry in fexamples:
                #         print(entry)
                for line in fsorries.splitlines():
                    # print(line)
                    if ("error" in line) or ("warning" in line):
                        dex1 = line.index(".lean:") + 6
                        line2 = line[dex1:]
                        dex2 = line2.index(":")
                        currLineNum = int(line2[:dex2])
                        # print("\tError detected at", currLineNum)
                        i = 0
                        for entry in fexamples:
                            if (entry[0] <= currLineNum):
                                i += 1
                                continue
                            elif examples[fexamples[i - 1][1]][1] == False:
                                current = examples[fexamples[i - 1][1]]
                                fexamples[i - 1][2] = False
                                perfect = False
                                current[2] = False
                                # print("\t\t->", fexamples[i - 1][0])
                                break
                            else:
                                # print("\t\tAll is forgiven!")
                                break
                        else:
                            current = examples[fexamples[i - 1][1]]
                            fexamples[i - 1][2] = False
                            perfect = False
                            current[2] = False
                            # print("\t\t->", fexamples[i - 1][0])

                if perfect:
                    os.replace(ffilename, os.path.join(submissionpath, "Perfect", filename))
                    print("\tPerfect!")
                else:
                    os.replace(ffilename, os.path.join(submissionpath, "For Review", filename))
                    print("\tNeeds review: ", end="")
                    score = 100
                    for entry in examples:
                        if entry[2]:
                            if entry[1]:
                                print("t", end="")
                            else:
                                print("T", end="")
                        else:
                            if entry[1]:
                                print("f", end="")
                            else:
                                print("F", end="")
                                score -= (float(score) / float(numExamples))
                    print(" Total score:", score)

os.remove(os.path.join(submissionpath, tempFile))