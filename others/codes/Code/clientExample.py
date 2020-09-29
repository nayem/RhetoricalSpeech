#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
clientExample.py

(C) 2017 by Damir Cavar <damir@cavar.me>

The client receives a str-objct with the pickled object. This string is encoded to a byte-object and
unpickled to an exampleClass object.
"""


import pickle
import xmlrpc.client
from exampleClass import exampleClass



def main(text):
    """Main function."""

    print("Client:", text)

    s = xmlrpc.client.ServerProxy('http://localhost:9001')
    res = pickle.loads(s.parse(text).encode())
    print("A:", res.getA(), "\tB:", res.getB())
    print("Returned", res)



if __name__=="__main__":
    main("some test text")

