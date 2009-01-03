#! /usr/bin/env python

import sys

from Pyro.EventService.Clients import Publisher
from Pyro.errors import NamingError
import Pyro.core

CHAT_SERVER_GROUP = ":ChatBox-ES"
CHAT_SERVER_NAME = CHAT_SERVER_GROUP+".Server"

class ChatBox(Pyro.core.ObjBase, Publisher):

	def __init__(self):
		Pyro.core.ObjBase.__init__(self)
		Publisher.__init__(self)
		self.channels = {}
		self.nicks = []

	def getChannels(self):
		return self.channels.keys()

	def getNicks(self):
		return self.nicks

	def join(self, channel, nick):
		if nick in self.nicks:
			raise ValueError,'this nick is already in use'
		if not self.channels.has_key(channel):
			print 'CREATING NEW CHANNEL',channel
			self.channels[channel]=('ChatBox.Channel.'+channel,[])
		self.channels[channel][1].append(nick)
		self.nicks.append(nick)
		print nick,'JOINED',channel
		self.publish(self.channels[channel][0],('SERVER','** '+nick+' joined **'))
		return self.channels[channel]  # return the eventTopic for this channel

	def leave(self, channel, nick):
		if not self.channels.has_key(channel):
			print 'IGNORED UNKNOWN CHANNEL',channel
			return
		self.channels[channel][1].remove(nick)
		self.publish(self.channels[channel][0],('SERVER','** '+nick+' left **'))
		if len(self.channels[channel][1])<1:
			del self.channels[channel]
			print 'REMOVED CHANNEL',channel
		self.nicks.remove(nick)
		print nick,'LEFT',channel
		

def main():
	Pyro.core.initServer()
	daemon = Pyro.core.Daemon()
	ns = Pyro.naming.NameServerLocator().getNS()
	daemon.useNameServer(ns)

	try:
		ns.createGroup(CHAT_SERVER_GROUP)
	except NamingError:
		pass
	try:
		ns.unregister(CHAT_SERVER_NAME)
	except NamingError:
		pass

	uri=daemon.connect(ChatBox(),CHAT_SERVER_NAME)

	print 'Server up!'
	daemon.requestLoop()


if __name__=='__main__':
	main()

# vim: set expandtab shiftwidth=4 softtabstop=4 textwidth=79:
