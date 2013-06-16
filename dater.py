#!/usr/bin/env python3

# ircecho.py
# Copyright (C) 2011 : Robert L Szkutak II - http://robertszkutak.com
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import sys
import socket
import string
import random
import re
from settings import *
from labmit import *

readbuffer = ""

s=socket.socket( )
s.connect((HOST, PORT))
f = s.makefile()

def send(l):
	s.send((l+'\r\n').encode('UTF-8'))

send("NICK {}".format(NICK))
send("USER {} {} bla :{}".format(IDENT, HOST, REALNAME))
send("JOIN {}".format(CHANNEL))
send("PRIVMSG {} :Hello Master".format(MASTER))
send("PRIVMSG NickServ : IDENTIFY {}".format(NICKSERV_PASSWORD))

class willi:
	def __init__(self):
		self.h = None
		self.l = None

	def characterise(self, thing):
		if not self.h:
			send('PRIVMSG willi :karma #c-base')
			line = f.readline()
			print('willi rx:', line)
			d = re.match('[^ ]+ [^ ]+ [^ ]+ :Highest karma: "[^"]*" \((?P<highest>-?\d*)\), "[^"]*" \(-?\d*\), and "[^"]*" \(-?\d*\).  Lowest karma: "[^"]*" \((?P<lowest>-?\d*)\), "[^"]*" \(-?\d*\), and "[^"]*" \(-?\d*\).', line).groupdict()
			self.h = int(d['highest'])
			self.l = int(d['lowest'])
		send('PRIVMSG willi :karma #c-base '+thing)
		_,_,_,_,k = f.readline().split()
		k = int(k)
		print('h|l|k:', self.h, self.l, k)
		if k>0:
			return k/self.h, k
		else:
			return -k/self.l, k

w = willi()

def lookup(value):
	if value == 0:
		value = 1
	value = value/abs(value)*abs(value)**(1/GAMMA)
	var = round(random.normalvariate(len(LABMIT)*(value+1)/2, len(LABMIT)/40))
	if var<0:
		var = 0
	if var>=len(LABMIT):
		var = len(LABMIT)-1
	var = len(LABMIT)-1-var
	print('value', value, LABMIT[var], var)
	return LABMIT[var]
	
while True:
	line = f.readline()
	print('RX:', line.rstrip())
	line = line.rstrip()
	line = line.split()

	if(line[0] == "PING"):
		send("PONG {}".format(line[1]))
	if(line[1] == "PRIVMSG"):
		#:jaseg!jaseg@gateway/shell/c-base/x-qrbrznfnybspczva => jaseg
		sender = line[0].split('!')[0][1:]
		message = ' '.join(line[3:])[1:]
		if line[2][0] in ['!', '#']: # message from a channel
			print('rx message ({}):'.format(sender), message)
			if re.match('^[.!#]characterise \w+', message):
				thing = message.split()[1]
				print('characterising', thing)
				try:
					value, karma = w.characterise(thing)
					l = []
					for e in [ lookup(value) for i in range(3) ]:
						if not e in l:
							l.append(e)
					k = l[0]
					if len(l) == 3:
						k += ', ' + l[1]
					if len(l) >= 2:
						k += ' and ' + l[-1]
					send('PRIVMSG {} :{} ({}): {}.'.format(line[2], thing, karma, k))
				except Exception as e:
					print('Error while characterising:', e)
					send("PRIVMSG {} :I'm sorry {}. I'm afraid I can't do that.".format(line[2], sender))
		else:
			print('rx query ({}):'.format(sender), message)

