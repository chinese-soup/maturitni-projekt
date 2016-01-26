#!/usr/bin/env python3
# coding=utf-8

import os, sys


class IRCSide(object):
	"""IRCSide"""
	def __init__(self, arg):
		super(IRCSide, self).__init__()
		self.arg = arg
		
	def add_server(self, name, server, port, ssl_bool, password):
		print("add_server({},{},{},{},{}, {})".format(self, name, server, port, ssl_bool, password))

class IRCServerConnection():
	def __init__(self, name, server, port, ssl_bool, password):
		name = self.name
		server = self.server
		port = self.port
		ssl_bool = self.ssl_bool
		password = self.password
		print(name, server, port, ssl_bool, password)
		
class WSocket(object):
	"""WSocket"""
	def __init__(self, arg):
		super(WSocket, self).__init__()
		self.arg = arg
		
if __name__ == "__main__":
	aparser = argparse.ArgumentParser()
	aparser.add_argument("--port", "-p",
		help="Specify a listen port.")#, default=13579)
	aparser.add_argument("--ui", "-i",
		help="Choose an interface. Available options: none (default)|text|curses.")
	aparser.add_argument("--timeout", "-t",
		help="Force a non-default (3 second) timeout for the request. (Use if you are running into timeout exceptions a lot.)")
	aparser.add_argument("command", nargs="?") # TODO: flag this as optional when using --ui text | curses ofc
	
	irc_side = IRCside()
	print irc_side 

	args = aparser.parse_args()
