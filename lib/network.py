#! /usr/bin/env python

import threading
import thread

from Pyro.EventService.Clients import Publisher, Subscriber
from server import CHAT_SERVER_NAME
from threading import Thread
import Pyro.core
from Pyro.errors import NamingError, ConnectionClosedError

# Hard-coded event server which should probably be configurable.
HOSTNAME = "localhost:9090"

class Publisher(object):

    """Generic Publisher for publishing messages."""

    def __init__(self, nick):
        self.nick = nick
        Pyro.core.initClient(banner=False)
        locator = Pyro.naming.NameServerLocator()
        ns = locator.getNS()
        uri = ns.resolve(Pyro.constants.EVENTSERVER_NAME)
        self.eventservice = Pyro.core.getProxyForURI(uri)
        
    def publish(self, topic, msg):
        self.eventservice.publish([topic], (self.nick, msg))

class Subscriber(Pyro.EventService.Clients.Subscriber):

    class _SubscriberThread(threading.Thread):

        def __init__(self, subscriber):
            threading.Thread.__init__(self)
            self.setDaemon(True)
            self._subscriber = subscriber

        def run(self):
            self._subscriber.listen()

    def __init__(self, topics, nick, event_processor):
        self.nick = nick
        self.topics = topics
        Pyro.core.initClient(banner=False)
        Pyro.core.initServer(banner=False)
        Pyro.EventService.Clients.Subscriber.__init__(self)
        assert isinstance(event_processor, EventProcessor)
        self.event_processor = event_processor
        self.chatbox = None
    
    def connect(self):
        self.chatbox = Pyro.core.getProxyForURI('PYRONAME://'+HOSTNAME+'/'+CHAT_SERVER_NAME)
        self.subscribe(self.topics)
        self.chatbox.join(self.topics, self.nick)
        self.thread = self._SubscriberThread(self)
        self.thread.start()

    def disconnect(self):
        if self.chatbox is not None:
            self.chatbox.leave(self.topics, self.nick)
            self.abort()
            self.thread.join()

    def event(self, event):
        self.event_processor.process_event(event)

    def getNick(self):
        return self.nick

    def getNicks(self):
        return self.chatbox.getNicks()

    def getServer(self):
        return HOSTNAME

class EventProcessor(object):

    def process_event(self, event):
        raise NotImplementedError, '%s.process_event()' % self.__class_

# vim: set expandtab shiftwidth=4 softtabstop=4 textwidth=79:
