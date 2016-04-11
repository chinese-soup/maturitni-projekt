#!/usr/bin/env python3

import os, sys, argparse, signal

# my stuff
from server import server

# TODO: parallel connections

import threading

if __name__ == "__main__":
    aparser = argparse.ArgumentParser()
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
