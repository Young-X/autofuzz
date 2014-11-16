#!/usr/bin/env python

import os
import sys
import subprocess


def get_class(kls):
    parts = kls.split('.')
    module = ".".join(parts[:-1])
    m = __import__(module)
    for comp in parts[1:]:
        m = getattr(m, comp)
    return m


def capture_command(command):
    ''' run command and captures output '''
    try:
        res = subprocess.check_output(
            command,
            stderr=subprocess.STDOUT,
            shell=True
        )
    except subprocess.CalledProcessError as e:
        print("command returned error code " + str(e.returncode))
        print("    - output: " + e.output)
        res = e.output

    return res


def passthru_command(command):
    ''' run command and output on screen '''
    subprocess.call(command, shell=True)


rootDir = os.path.dirname(os.path.realpath(__file__))

if not os.path.isdir(rootDir + "/.fuzz-afl"):
    os.mkdir(rootDir + "/.fuzz-afl")

# TODO take 1 parameter, formula name
if len(sys.argv) < 2:
    print("ERROR: supply formula name")
    sys.exit()

formulaName = sys.argv[1]

try:
    formula = get_class("formulas." + formulaName + "." + formulaName)
except ImportError:
    print("ERROR: No such formula " + formulaName)
    sys.exit()

print("### " + formulaName)

formulaPath = ".cache/" + formulaName

# TODO remove assumption of git repository, need svn support, etc
gitPath = formulaPath + "/.git"
svnPath = formulaPath + ".svn"
if os.path.isdir(gitPath) or os.path.isdir(svnPath):
    # TODO if dir exist, do a "git pull" ? also make sure it is pristine
    print("Checkout found at " + gitPath + " or " + svnPath + ", TODO do update?")
else:
    print("### CHECKOUT " + formula.scmOrigin + " ...")

    getScm = formula.scmOrigin + " .cache/" + formulaName
    passthru_command(getScm)

# set current working dir to formulaPath
os.chdir(formulaPath)
# print("changed cwd to " + os.getcwd())

fuzzTarget = formula.target

if not os.path.isfile(fuzzTarget):    # TODO cli switch to force rebuild
    # if target not found, perform clean + build
    for cleanCmd in formula.clean:
        print("CLEAN # " + cleanCmd)
        capture_command(cleanCmd)

    for buildCmd in formula.build:
        print("BUILD # " + buildCmd)
        passthru_command(buildCmd)

if not os.path.isfile(fuzzTarget):
    print("ERROR cant find target " + fuzzTarget + ", giving up")
    sys.exit()

print("Found " + fuzzTarget + ", ready to fuzz")

# find a nonexisting out dir
outCounter = 1
while True:
    aflOutDir = rootDir + "/.fuzz-afl/" + formulaName + "-%04d" % outCounter
    if not os.path.isdir(aflOutDir):
        break
    outCounter += 1

# TODO prepare test cases from dataTypes list
aflInDir = rootDir + "/testcases/images/gif"
aflFuzzTarget = rootDir + "/" + formulaPath + "/" + fuzzTarget
aflFuzzTargetParam = formula.targetParam
fuzzCmd = "afl-fuzz -i " + aflInDir + " -o " + aflOutDir + " " + aflFuzzTarget + " " + aflFuzzTargetParam

print("FUZZ # " + fuzzCmd)
passthru_command(fuzzCmd)
