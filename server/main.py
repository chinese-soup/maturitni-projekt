#!/usr/bin/env python3
# coding=utf-8

import os, sys, argparse, signal

# my stuff
from server import server

# TODO: parallel connections

import threading


if __name__ == "__main__":
    aparser = argparse.ArgumentParser()
    aparser.add_argument("--port", "-p", help="Specify a listen port.")#, default=13579)
    aparser.add_argument("--timeout", "-t", help="Force a non-default (3 second) timeout for the request. (Use if you are running into timeout exceptions a lot.)")
    aparser.add_argument("--config", "-c", help="Select an alternative config file.")
    aparser.add_argument("userid", help="userid")
    args = aparser.parse_args()

    if args.userid:
        #irc_side = server.IRCSide(1)

        #irc_side2 = server.IRCSide(2)
        #irc_side.start()
        #irc_side2.start()
        
        i1 = threading.Thread(target=server.IRCSide, args=(1,))
        i2 = threading.Thread(target=server.IRCSide, args=(2,))
        i1.start()
        i2.start()

    else:
        print("This should never happen.")
