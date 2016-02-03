#!/usr/bin/python3.4
# coding=utf-8

import os, sys, argparse, signal

# my stuff
from server import server


# TODO: CHECK FOR USER VALIDATION

if __name__ == "__main__":
    aparser = argparse.ArgumentParser()
    aparser.add_argument("--port", "-p", help="Specify a listen port.")#, default=13579)
    aparser.add_argument("--timeout", "-t", help="Force a non-default (3 second) timeout for the request. (Use if you are running into timeout exceptions a lot.)")
    aparser.add_argument("--config", "-c", help="Select an alternative config file.")
    args = aparser.parse_args()

    irc_side = server.IRCSide()
    irc_side.start()

