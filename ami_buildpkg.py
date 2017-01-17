#!/usr/bin/env python3
#
# Take a directory path that points to our package, gather up a few
# pieces of config data and then invoke the Web2Executable
# command_line.py to build a package for it.
#
# Arguments:
#    path - the path to where the existing package code can be found
#    outdir - the directory (underneath 'path') into which we are to
#        put our build products.
# 
# Steve Kierstead, AMI Entertainment Network, Inc, 1/2017

import sys
import argparse
import os.path
import json
import re
import subprocess
import logging

def complain(msg):
    logging.error(str(msg))
    sys.exit(1)

def getValuesFromJson(path):
    '''
        Given a path to a json file, parse/read that file and get
        the values we want from it.  If any of those values are
        missing, or if anything else goes wrong, bail.  If all goes
        well, RETURN a dict containing the values we have found.

        Values we are looking for:
            "main" - we put this into the returned dict with key "main"
            "dependencies"/"nw" - we put this under key "nwver"
    '''
    with open(path) as f:
        jsondata = json.load(f)

    rval = dict()

    ######
    # get the value for "main"
    if "main" in jsondata.keys():
        rval["main"] = jsondata["main"]
    else:
        complain("Can't find \"main\" in {}".format(path))

    ######
    # get the value for "nwver"
    if "dependencies" in jsondata.keys() and "nw" in jsondata["dependencies"].keys():
        # Sometimes this string starts with a caret ('^'), which we
        # need to get rid of.
        raw = jsondata["dependencies"]["nw"]
        regex = re.compile(r'(\^)*(.*)$')

        rval["nwver"] = re.match(regex, raw).group(2)
    else:
        complain("Can't find \"dependencies/nw\" in {}".format(path))

    return rval

def main():
    logging.basicConfig(format="%(asctime)s: %(levelname)s: %(message)s",
                        level=logging.DEBUG)

    parser = argparse.ArgumentParser()

    parser.add_argument("path",
            help="Path to where code to be packaged lives")

    parser.add_argument("outdir",
            help="Directory (under 'path') where we put our results")

    args = parser.parse_args()

    # Be sure the directory (args.path) exists
    pkgDir = args.path
    if not os.path.isdir(pkgDir):
        complain("Not a directory: {}.".format(pkgDir))
    else:
        # Be sure it contains a package.json file
        packageFile = os.path.join(pkgDir, "package.json")
        web2exeDir = os.path.dirname(os.path.abspath(__file__))
        cmdLinePath = os.path.join(web2exeDir, "command_line.py")
        if not os.path.isfile(packageFile):
            complain("Unable to find \"{}\" file".format(packageFile))
        else:
            # Read the values we need from package.json
            cmdArgs = getValuesFromJson(packageFile)

            # Build the command we want to run
            cmdStr = [
                "python3.4",
                cmdLinePath,
                pkgDir,
                "--export-to", "linux-x32",
                "--nw-version", cmdArgs["nwver"],
                "--nw-compression-level", "9",
                "--output-dir", os.path.join(pkgDir, args.outdir),
                "--package-json", packageFile,
                "--main", cmdArgs["main"]
                ]

            # Run it
            logging.debug("cmdStr = {}".format(str(cmdStr)))
            result = subprocess.call(cmdStr)
            if (result != 0):
                complain("Something went wrong in running the command: {}".format(str(cmdStr)))

if __name__ == "__main__":
    main()
