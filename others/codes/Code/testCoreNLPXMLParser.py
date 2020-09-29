#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
testCoreNLPXMLParser.py

(C) 2017 by Damir Cavar <damir@cavar.me>

This script tests the functionality of the CoreNLPXMLServer instance.

"""


__license__ = """Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License."""
__revision__ = " $Id: testCoreNLPXMLParser.py 2 2017-07-25 14:32:00Z damir $ "
__docformat__ = 'reStructuredText'
__author__ = 'Damir Cavar <damir@cavar.me>'
__version__ = '0.1'



import sys, datetime, glob, configparser, argparse
from LingData import Sentence, LingData, Clause, Token
from SemDiscUtils import decodeReturn
import xmlrpc.client


port = 9007
host = "localhost"

conffile = "config.ini"


def parseConfiguration(conff=conffile):
    """
    Parse the config.ini and set the parameters.
    """
    global port, host
    config = configparser.ConfigParser()
    config.read(conff)
    if "corenlpxml" in config.sections():
        if "host" in config["corenlpxml"]:
            host = config["corenlpxml"]["host"]
            print("Setting configuration: CoreNLPXML host=" + host)
        if "port" in config["corenlpxml"]:
            port = config["corenlpxml"]["port"]  # this is a string!
            print("Setting configuration: CoreNLPXML port=" + port)
    return port, host


def main(fname, example=""):
    """Main function."""
    global host, port
    if fname:
        print(fname)
    print("-" * 30)

    if example:
        s = xmlrpc.client.ServerProxy('http://' + host + ':' + str(port))

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
