#!/usr/bin/env python3
# -*- coding: UTF-8 -*-


"""
(C) 2017 by D. Cavar <dcavar@iu.edu>

Testing Foma in Python with NLTK pre-processing

Make sure that the script is either executable or that you can run it with your Python 3.x interpreter.

I recommend that you use Anaconda, because it has all modules preinstalled, except of the foma module.

Place the foma.py module somewhere in your path or module location. This is not the same as the one on the public
GitHub, it is patched to work with Python 3.x
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
__revision__ = " $Id: morphanalyzer.py 2 2017-07-25 14:32:00Z damir $ "
__docformat__ = 'reStructuredText'
__author__ = 'Damir Cavar <damir@cavar.me>'
__version__ = '0.2'


import foma, sys, configparser, argparse, logging, logging.handlers
from nltk import word_tokenize
from nltk.tokenize import sent_tokenize
from nltk import pos_tag
from xmlrpc.server import SimpleXMLRPCServer
from SemDiscUtils import encodeReturn, decodeReturn
from LingData import LingData, Sentence, Clause, Token


host = "localhost"
port = "9006"
fst = "eng.fst"
fsm = None
logfile = "morphoanalyzer.log"
n = 6 #: n-gram model size


conffile = "config.ini"


def mainClient(fname):
    """
    :param fname:
    :return:
    """
    text = ""
    try:
        ifp = open(fname, mode='r', encoding='utf-8')
        text = ifp.read()
        ifp.close()
        logging.info("Read file: {}".format(fname))
    except IOError:
        logging.error("Cannot read file: {}".format(fname))
    parse(text)


def parse(text):
    """
    :param text:
    :return:
    """
    global fsm, n
    logging.debug("Processing text:")
    logging.debug(text)

    myLD = LingData()
    myLD.NLPID = "MorphoAnalyzer"

    sentences = sent_tokenize(text)

    res = []
    for s in sentences:
        logging.debug("Processing: {}".format(s.strip()))
        tokens = word_tokenize(s)
        tagged = pos_tag(tokens)
        if tagged[0][1] != 'NNP' and str.isupper(tokens[0][0]) and str.islower(tokens[0][1:]):
            tokens[0] = tokens[0].lower()
        res0 = []
        for i in range(1, n + 1):
            for j in range(len(tokens)-i+1):
                toks = " ".join(tokens[j:i+j])
                result = list(fsm.apply_up(str.encode(toks)))
                if len(result) == 0:
                    res1 = ""
                    if i == 1:
                        res1 += "\t".join( (str(j), str(j+i), toks) ) + "\t"
                        if toks == tagged[j][1]:
                            res1 += toks + "+Punct"
                        elif tagged[j][1] == 'JJ':
                            res1 += toks.lower() + "+Adj"
                        elif tagged[j][1] == 'NNP':
                            res1 += toks + "+N"
                        elif tagged[j][1] == 'CC':
                            res1 += toks + "+Conj"
                        else:
                            res1 += tagged[j][1]
                    res0.append(res1)
                    logging.debug("Processed: {}".format(res1))
                else:
                    res0.append( "\t".join( (str(j), str(j + i), toks, ", ".join([ i.decode('utf-8') for i in result ])) ) )
                    logging.debug("Processed: {}".format(res0[-1]))
        for i in res0:
            print(i)
        res.append(res0)
        logging.debug("Processed sentence: {}".format(s.strip()))
    return encodeReturn(res)


def mainServer():
    """Start the Dispatcher in Server mode."""
    global port, host

    # start the XML-RPC server
    server = SimpleXMLRPCServer((host, int(port)), allow_none=True)
    server.register_introspection_functions()
    server.register_function(parse)

    logging.info('Serving XML-RPC on {} port {}'.format(host, port))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logging.info("Interrupt received, exiting.")
        sys.exit(0)


def parseConfiguration(conff=conffile):
    """

    :param conff:
    :return:
    """
    global host, port, fst, logfile

    # read configuration
    config = configparser.ConfigParser()
    config.read(conff)

    # read CoreNLP configuration and fire it up
    if "morphoanalyzer" in config.sections():
        if "host" in  config["morphoanalyzer"]:
            host = config["morphoanalyzer"]["host"]
        if "port" in config["morphoanalyzer"]:
            port = config["morphoanalyzer"]["port"] # this is a string!
        if "fst" in config["morphoanalyzer"]:
            fst = config["morphoanalyzer"]["fst"]
        if "logfile" in config["morphoanalyzer"]:
            logfile = config["morphoanalyzer"]["logfile"]


if __name__=="__main__":
    # command line arguments overwrite config-file parameters
    parser = argparse.ArgumentParser(prog="MorphoAnalyzer", description='Command line arguments.', epilog='')
    parser.add_argument('-c', '--config', dest="conffile", default=conffile, help="Alternative config.ini file name")
    parser.add_argument('-t', '--test', dest='test', action='store_true', help="Run in test mode") # just a flag
    args = parser.parse_args()

    # if command line config ini specified, read it
    if conffile != args.conffile:
        conffile = args.conffile
    parseConfiguration(conffile)

    #logging.basicConfig(filename=logfile, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
    logging.basicConfig(filename=logfile, filemode='w', format='%(asctime)s - %(levelname)s - %(message)s', level=logging.DEBUG)

    fsm = foma.FST.load(fst.encode())
    logging.info("Loaded FST {}".format(fst))

    if (args.test):
        print("Starting in test mode...")
        mainClient(args.tfname)
    else:
        logging.info("Starting as XML-RPC server...")
        mainServer()
