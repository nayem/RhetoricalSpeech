#!/usr/bin/env python3
# -*- coding: UTF-8 -*-


"""
testDispatcher.py

(C) 2017 by Damir Cavar <damir@cavar.me>
"""


import sys, glob, configparser, datetime, argparse
from SemDiscUtils import encodeReturn, decodeReturn
import xmlrpc.client


conffile = "config.ini"


def parseConfiguration(conf=conffile):
    """Parse the config.ini and set the parameters."""
    port = 9007
    host = "localhost"
    #logfile = "spaCy.log"
    config = configparser.ConfigParser()
    config.read(conf)
    if "spacy" in config.sections():
        if "host" in config["spacy"]:
            host = config["spacy"]["host"]
            print("Setting configuration: spaCy host=" + host)
        if "port" in config["spacy"]:
            port = config["spacy"]["port"]  # this is a string!
            print("Setting configuration: spaCy port=" + port)
    #    if "logfile" in config["spacy"]:
    #        logfile = config["spacy"]["logfile"]
    #        print("Setting configuration: logfile=" + logfile)
    return port, host


def main(fname="", example=""):
    """Main function."""
    port, host = parseConfiguration()
    print(fname)
    if not example:
        example = "Tim Cook is the CEO of Apple. He is not the CEO of Google."
    s = xmlrpc.client.ServerProxy('http://' + host + ':' + port)
    res = decodeReturn(s.parse(example))
    print("NLP ID:", res.NLPID)
    print("Timestamp:", datetime.date.fromtimestamp(res.parseTime))
    print("-" * 30)
    for s in res.tokenList:
        print(s.word)


if __name__=="__main__":
    parser = argparse.ArgumentParser(prog="testCoreNLPXMLParser", description='Command line arguments.', epilog='')
    parser.add_argument('-c', '--config', dest="conffile", default=conffile, help="Alternative config.ini file name")
    parser.add_argument('files', nargs='?', help="File names to process")
    args = parser.parse_args()

    if args.conffile != conffile:
        port, host = parseConfiguration(args.conffile)
    else:
        port, host = parseConfiguration()

    if args.files:
        for fname in args.files:
            main(fname)
    else:
        main("", example = "Tim Cook is the CEO of Apple. He is not the CEO of Google.")

