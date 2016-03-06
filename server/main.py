#!/usr/bin/env python3
# coding=utf-8

import os, sys, argparse, signal

# my stuff
from server import server

# TODO: parallel connections


if __name__ == "__main__":
    aparser = argparse.ArgumentParser()
    aparser.add_argument("--port", "-p", help="Specify a listen port.")#, default=13579)
    aparser.add_argument("--timeout", "-t", help="Force a non-default (3 second) timeout for the request. (Use if you are running into timeout exceptions a lot.)")
    aparser.add_argument("--config", "-c", help="Select an alternative config file.")
    aparser.add_argument("userid", help="userid")
    args = aparser.parse_args()

    if args.userid:
        irc_side = server.IRCSide(args.userid)
        irc_side.start()
    else:
        print("This should never happen.")
