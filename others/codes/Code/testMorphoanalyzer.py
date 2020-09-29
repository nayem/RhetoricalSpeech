#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
testMorphoanalyzer.py

(C) 2017 by Damir Cavar <damir@cavar.me>

The client receives a str-objct with the pickled object. This string is encoded to a byte-object and
unpickled to an exampleClass object.
"""


import xmlrpc.client, configparser, argparse
from SemDiscUtils import decodeReturn


conffile = "config.ini"
port = 9007
host = "localhost"


def parseConfiguration(conff=conffile):
    """
    Parse the config.ini and set the parameters.
    """
    global port, host
    config = configparser.ConfigParser()
    config.read(conff)
    if "morphoanalyzer" in config.sections():
        if "host" in config["morphoanalyzer"]:
            host = config["morphoanalyzer"]["host"]
            print("Setting configuration: Morphoanalyzer host=", host)
        if "port" in config["morphoanalyzer"]:
            port = config["morphoanalyzer"]["port"]  # this is a string!
            print("Setting configuration: Morphoanalyzer port=", port)
    return port, host


def main(text):
    """Main function."""
    global host, port
    print("Client:", text)

    s = xmlrpc.client.ServerProxy('http://{}:{}'.format(host, port))
    res = decodeReturn(s.parse(text))
    print("Returned", res)


if __name__=="__main__":
    parser = argparse.ArgumentParser(prog="testMorphoanalyzer", description='Command line arguments.', epilog='')
    parser.add_argument('-c', '--config', dest="conf", default=conffile, help="Alternative config.ini file name")
    args = parser.parse_args()

    if args.conf != conffile:
        conffile = args.conf
    port, host = parseConfiguration(conff=conffile)
    main("John Doe loves Mary Smith.")
