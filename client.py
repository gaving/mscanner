#! /usr/bin/env python

from lib import scanner
import os
from optparse import OptionParser

from Pyro.EventService.Clients import Publisher, Subscriber
from server import CHAT_SERVER_NAME
from threading import Thread
import Pyro.core
from Pyro.errors import NamingError, ConnectionClosedError

class Client(Publisher, Subscriber):

    def __init__(self):
        Publisher.__init__(self)
        Subscriber.__init__(self)
        self.chatbox = Pyro.core.getProxyForURI('PYRONAME://localhost:9090/' + CHAT_SERVER_NAME)

        if os.path.isdir(args[0]):
            self.scanner = scanner.Scanner()
            self.scanner.clear()
            [self.scanner.scan(arg) for arg in args]

    def event(self, event):
        pass

    def chooseChannel(self):
        nicks = self.chatbox.getNicks()

        if nicks:
            print 'The following people are currently connected: ',', '.join(nicks)

        self.profile = 'profile'
        self.nick = raw_input('Choose a nickname: ')
        (self.eventTopic, people) = self.chatbox.join(self.profile, self.nick)
        self.subscribe(self.profile)
        self.inputThread=Thread(target=self.handleInput)
        self.inputThread.start()
        try:
            self.listen()
        except KeyboardInterrupt:
            print 'Shutting down... (press enter)'
            self.abort()
            self.inputThread.join()

    def handleInput(self):
        try:
            print "Publishing database.."
            self.database = self.scanner.toList()
            self.publish(self.profile, (self.nick, self.database))
            print "Press enter to republish database or /quit to quit"
            try:
                while not self.abortListen:
                    line = raw_input(' ')
                    if line == '/quit':
                        break
                    print "Publishing database.."
                    self.publish(self.profile, (self.nick, self.database))
            except EOFError:
                pass
        finally:
            self.chatbox.leave(self.profile, self.nick)
            self.abort()

def main():
    chatter = Client()
    chatter.chooseChannel()

parser = OptionParser(usage="%prog path", version="0.1",
        description="Scan music library")
options, args = parser.parse_args()

if len(args) < 1:
    parser.error("too few arguments")

if __name__=="__main__":
    main()

# vim: set expandtab shiftwidth=4 softtabstop=4 textwidth=79:
