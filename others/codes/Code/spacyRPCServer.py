#!/usr/bin/env python3
# -*- coding: UTF-8 -*-


"""
spacyRPCServer.py

(C) 2017 by Damir Cavar <damir@cavar.me>

This code runs Spacy in server mode as an XML-RPC server.

The defaults are:
- port = 8000
- host = "localhost"
- language = 'en'

Prerequisites:
- Python 3.x
- Installed modules: spacy, argparse


\copyright Copyright 2017 by Damir Cavar

\license{Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.}
"""


import sys, configparser, argparse, logging, spacy
from xmlrpc.server import SimpleXMLRPCServer
from SemDiscUtils import encodeReturn, decodeReturn
from Spacy2LingData import translateToLingData


# Defaults
port = 9001
host = "localhost"
language="en"
logfile = "spaCy.log"
conffile = "config.ini"

nlp = None


def usage():
    logging.info('Usage called.')


def parseConfiguration(conf=conffile):
    """Parse the config.ini and set the parameters."""

    global host, port, language, logfile

    config = configparser.ConfigParser()
    config.read(conf)
    if "spacy" in config.sections():
        if "host" in config["spacy"]:
            host = config["spacy"]["host"]
        if "port" in config["spacy"]:
            port = config["spacy"]["port"]  # this is a string!
        if "language" in config["spacy"]:
            language = config["spacy"]["language"]
        if "logfile" in config["spacy"]:
            logfile = config["spacy"]["logfile"]


def main():
    pass


def parse(text):
    # print('Received text:\n', text)
    global nlp
    logging.debug('Received text:\n' + text)
    ''' test case
    res = []
    doc = nlp(text, parse=True)
    for sentence in doc.sents:
        res.append( tuple( [ x.text for x in sentence ] ) )
    logging.debug('Result:\n' + repr(res))
    '''
    logging.debug("Calling translateToLingData")
    ld = translateToLingData(nlp, text)
    logging.debug("Returning result.")
    return encodeReturn(ld)


if __name__=="__main__":

    # overwrite with parsed arguments
    parser = argparse.ArgumentParser(prog="spacyRPC", description='Command line arguments.', epilog='')
    parser.add_argument('-c', '--config', dest="conffile", default=conffile, help="Alternative config.ini file name")
    args = parser.parse_args()

    # parse the config first
    if args.conffile != conffile:
        parseConfiguration(args.conffile)
    else:
        parseConfiguration()

    # start logging
    print("Logfile:", logfile)
    logging.basicConfig(filename=logfile, filemode='w', format='%(asctime)s - %(levelname)s - %(message)s', level=logging.DEBUG)
    logging.debug('Loading spaCy...')

    # load spacy into RAM
    nlp = spacy.load(language)

    # set up XML-RPC server
    server = SimpleXMLRPCServer((host, int(port)), allow_none=True)
    server.register_introspection_functions()
    server.register_function(parse)
    logging.debug('spacyRPCServer Serving XML-RPC on {} port {}'.format(host, port))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logging.debug("Keyboard interrupt received, exiting.")
        sys.exit(0)
