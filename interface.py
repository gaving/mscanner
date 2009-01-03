#! /usr/bin/env python

import os
import sys
import re
import time
import pprint
import pickle
import getpass
from time import gmtime, strftime

import pygtk
pygtk.require("2.0")

import gtk
import gtk.glade
import gobject

if gtk.gtk_version < (2, 8):
    import warnings

    msg = ('''This program was developed and tested with version 2.8.18 of \
            gtk.  You are using version %d.%d.%d.  Your milage may vary.'''
           % gtk.gtk_version)
    warnings.warn(msg)

# python 2.4
from operator import itemgetter
from optparse import OptionParser

from TreeViewTooltips import *

from lib import associator
from lib import chart
from lib import network
from lib import scanner

DATA_FILE = "db.txt"
DATABASES = {}

class Interface:
    """This class handles the actual interface of the application. """

    class ColumnTips(TreeViewTooltips):

        def __init__(self, genre_column, type):
            self.genre_col = genre_column
            self.type = type
            TreeViewTooltips.__init__(self)

        def get_tooltip(self, view, column, path):

            if column is self.genre_col:
                if self.type == 'GENRE':
                    model = view.get_model()
                    count = model[path][2]
                    return '<big>%d tracks</big>' % count
                elif self.type == 'RATING':
                    model = view.get_model()
                    database = model[path][4]
                    if database:
                        organised_artists = database.organise()
                        return '<big>Common artists: %s</big>' % len(organised_artists)

        def XX_location(self, x, y, w, h):
            return x + 10, y - (h + 10)

    class EventConsumer(network.EventProcessor):

        def __init__(self, nick):
            self.nick = nick

        def process_event(self, event):
            (nick, profile) = event.msg
            if nick != self.nick:
                if event.subject == 'profile':
                    print "! Received database from %s with %d items" % (nick,
                            len(profile))
                    DATABASES[nick] = profile

    def __init__(self):
        self.wTree = gtk.glade.XML('glade/main.glade')

        dic = {
            "on_window_destroy" : self.onClose,
            "on_refresh_button_clicked" : self.onRefresh,
            "on_connect_button_clicked" : self.onConnect,
            "on_apply_button_clicked" : self.onApply,
            "on_home_button_clicked" : self.onHome,
            "on_friends_button_clicked" : self.onFriends,
            "on_clear_button_clicked" : self.onClear,
            "on_file_quit_activate" : self.onClose,
            "on_view_chart_activate" : self.onChart,
            "on_view_home_activate" : self.onHome,
            "on_view_friends_activate" : self.onFriends,
        } 

        self.wTree.signal_autoconnect(dic)
        self.username = getpass.getuser()

        self.state = State()
        self.scanner = scanner.Scanner()

        # The 'profile' channel is where we do the exchanging of profiles
#        self.subscriber = network.Subscriber("profile", 
#                self.username, self.EventConsumer(self.username))
       
        self.scrolledWindows = {}

        self.scrolledWindows['home'] = self.wTree.get_widget("scrolledwindow1")
        self.genreView = self.wTree.get_widget("genreView")
        self.progressBar = self.wTree.get_widget("progressbar")
        self.statusBar = self.wTree.get_widget("statusbar")

        self.refreshButton = self.wTree.get_widget("refresh_button")
        self.connectButton = self.wTree.get_widget("connect_button")
        self.friendsButton = self.wTree.get_widget("friends_button")
        self.applyButton = self.wTree.get_widget("apply_button")
        self.applyButton.set_property('sensitive', False)

        self.viewFriendsMenuItem = self.wTree.get_widget("view_friends")
        self.viewFriendsMenuItem.set_property('sensitive', False)

        self.vBox = self.wTree.get_widget("vbox1")
        self.friendsvisible = False

        self.addColumn("Genre", 0)
        column = self.addProgress("Percentage of Library", 1)
        tips = self.ColumnTips(column, 'GENRE')
        tips.add_view(self.genreView)

        self.genreList = gtk.ListStore(str, int, object)
        self.genreView.set_model(self.genreList)

        self.checkStatus()

    def addColumn(self, title, columnId):
        column = gtk.TreeViewColumn(title, gtk.CellRendererText(), text=columnId)
        column.set_resizable(True)		
        self.genreView.append_column(column)

    def addProgress(self, title, columnId):
        column = gtk.TreeViewColumn(title)
        renderer = gtk.CellRendererProgress()
        column.pack_start(renderer, expand=True)
        column.set_expand(True)
        column.add_attribute(renderer, 'value' , 1)
        self.genreView.append_column(column)
        return column
    
    def checkStatus(self):
        if self.state.isUpdating():
            self.updateStatus("Scanning..")
        elif self.state.isConnected():
            self.updateStatus("Connected to '%s' as '%s'." %
                    (self.subscriber.getServer(), self.subscriber.getNick()))
        elif not self.state.isConnected():
            self.updateStatus("Disconnected.")
        else:
            self.updateStatus("Idle.")

    def connect(self):
        self.subscriber.connect()

    def disconnect(self):
        self.subscriber.disconnect()

    def onApply(self, widget):
        db = self.scanner.toList()

        publisher = network.Publisher(self.username)
        publisher.publish("profile", db)
        
        self.associator = associator.Associator(self.getGenres())

    def onConnect(self, widget):
        if self.state.isConnected():
            self.state.setConnected(False)
            self.disconnect()
        else: 
            self.state.setConnected(True)
            self.connect()

        self.checkStatus()
        self.toggleConnectionStatus()

    def onChart(self, widget):
        genreList = self.getGenres()
        thechart = chart.Chart()
        thechart.makeChart(genreList)

    def onClear(self, widget=None):
        self.genreList.clear()
        self.toggleListStatus()

    def onClose(self, widget, huh=None):
        self.disconnect()
        gtk.main_quit()

    def onHome(self, widget):
        
        if self.friendsvisible:
            self.vBox.remove(self.scrolledWindows['friends'])
            self.vBox.add(self.scrolledWindows['home'])
            self.vBox.reorder_child(self.scrolledWindows['home'], 2)
            self.friendsvisible = False
            return

    def onFriends(self, widget):

        if not self.friendsvisible:
            if self.scrolledWindows.has_key('friends'):
                self.vBox.remove(self.scrolledWindows['home'])
                self.vBox.add(self.scrolledWindows['friends'])
                self.vBox.reorder_child(self.scrolledWindows['friends'], 2)
                self.friendsvisible = True
            else:
                self.vBox.remove(self.scrolledWindows['home'])

                self.scrolledWindows['friends'] = gtk.ScrolledWindow()
                self.scrolledWindows['friends'].set_shadow_type(gtk.SHADOW_IN)
                self.scrolledWindows['friends'].set_property('hscrollbar-policy', gtk.POLICY_AUTOMATIC)
                self.scrolledWindows['friends'].set_property('vscrollbar-policy', gtk.POLICY_AUTOMATIC)

                self.model = gtk.ListStore(gtk.gdk.Pixbuf, str, str, str,
                        object, str)
                self.treeview = gtk.TreeView(self.model)
                column = gtk.TreeViewColumn("?", gtk.CellRendererPixbuf(),
                        pixbuf=0)
                column1 = gtk.TreeViewColumn("User", gtk.CellRendererText(),
                        text=1, foreground=3)
                column2 = gtk.TreeViewColumn("Tracks", gtk.CellRendererText(), 
                        text=2)
                column3 = gtk.TreeViewColumn("Last Seen", gtk.CellRendererText(), 
                        text=5)
                self.treeview.append_column(column)
                self.treeview.append_column(column1)
                self.treeview.append_column(column2)
                self.treeview.append_column(column3)
                self.treeview.set_headers_visible(True)

                self.treeview.connect("button-press-event",
                        self.onOpenTrackList)
                
                tips = self.ColumnTips(column2, 'RATING')
                tips.add_view(self.treeview)

                self.scrolledWindows['friends'].add(self.treeview)
                self.vBox.pack_start(self.scrolledWindows['friends'], True, True, 0)
                self.vBox.reorder_child(self.scrolledWindows['friends'], 2)
                self.scrolledWindows['friends'].show_all()

                self.friendsvisible = True

        self.updateFriends()            
    
    def onOpenTrackList(self, widget, event):
        if event.button == 1 and event.type == gtk.gdk._2BUTTON_PRESS:
            treeselection = self.treeview.get_selection()
            (model, iter) = treeselection.get_selected()
            name_of_data = self.model.get_value(iter, 4)

            if not name_of_data:
                return

            user_database = name_of_data.organise()
            my_database = self.scanner.organise()

            if not getattr(self, 'trackView', None):
                self.trackView = self.wTree.get_widget("trackView")
                column = gtk.TreeViewColumn("Track", gtk.CellRendererText(),
                        text=0, background=1)
                self.trackView.append_column(column)
                self.trackView.set_headers_visible(False)
            
            if not getattr(self, 'trackWindow', None):
                self.trackWindow = self.wTree.get_widget("user_window")
                self.trackWindow.set_size_request(300, 500)
                self.trackWindow.set_position(gtk.WIN_POS_CENTER)
            
            musicList = gtk.TreeStore(str, str)
            musicList.set_sort_column_id(0, gtk.SORT_ASCENDING)
            self.trackView.set_model(musicList)
           
            # This is the worst block of code written in the history of
            # programming
            for artist, album in user_database.items():
                # List albums
                colour = "#FFFF88"
                if my_database.has_key(artist):
                    colour = "#6BBA70"
                piter = musicList.append(None, [artist, colour])
                if album:
                    # List albums
                    for album, tracks in album.items():
                        try:
                            if my_database[artist].has_key(album):
                                colour = "#6BBA70"
                            else:
                                colour = "#FFFF88"
                        except KeyError:
                            colour = "#FFFF88"
                        piter2 = musicList.append(piter, [album, colour])
                        if tracks:
                            # List tracks
                            for track in tracks:
                                musicList.append(piter2, [track['title'], None])

            self.trackWindow.show_all()
    
    def onDeleteTrackList(self, widget, event):
        pass

    def onRefresh(self, widget):
        self.onClear()
        self.progressBar.set_property('visible', True)
        self.state.setUpdating(True)
        self.checkStatus()
        timer = gobject.timeout_add(100, self.progressTimeout, self)
        try:
            self.scanner.clear()
            [self.scanner.scan(arg, self.scan_cb) for arg in args]
        except KeyboardInterrupt:
            pass
        self.updateStatus("Finished scan. (Database of %d artists)" % 
                len(self.scanner.db))
        self.progressBar.set_property('visible', False)
        self.state.setUpdating(False)
        
        self.populateGenres()
   
    def getGenres(self, scanner=None):
        if not scanner:
            scanner = self.scanner

        genreList = []
        genres = sorted(scanner.getGenres().items(), 
                key=itemgetter(1), reverse=True)
        total = 0
        for x, y in genres:
            total += y
        for genre, count in genres:
            percent = 100*count/total
            genreList.append([genre, percent, count])

        return genreList

    def populateGenres(self):
        genres = self.getGenres()

        for genre, percent, count in genres:
            self.genreList.append([genre, percent, count])

        self.toggleListStatus()

    def progressTimeout(self, pbar):
        if self.state.isUpdating():
            self.progressBar.pulse()
            return True
        else:
            return False

    def scan_cb(self, current):
        self.statusBar.push(self.statusBar.get_context_id("statusbar"), 
                os.path.basename(current))

    def toggleListStatus(self):
        chartItem = self.wTree.get_widget("view_chart")
        clearButton = self.wTree.get_widget("clear_button")

        hasItems = len(self.genreList) > 0

        chartItem.set_property('sensitive', hasItems)
        clearButton.set_property('sensitive', hasItems)

    def toggleConnectionStatus(self):
        if self.state.isConnected():
            self.connectButton.set_stock_id(gtk.STOCK_DISCONNECT)
            self.friendsButton.set_property('sensitive', True)
            self.viewFriendsMenuItem.set_property('sensitive', True)
            self.applyButton.set_property('sensitive', True)
        else:
            self.connectButton.set_stock_id(gtk.STOCK_CONNECT)
            self.friendsButton.set_property('sensitive', False)
            self.viewFriendsMenuItem.set_property('sensitive', False)
            self.applyButton.set_property('sensitive', False)

    def updateFriends(self):
        self.model.clear()
        print "Scanning %d nicks" % len(self.subscriber.getNicks())
        for nick in self.subscriber.getNicks():
            database = None
            total = None
            icon = None
            time = strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
            if DATABASES.has_key(nick):
                database = DATABASES[nick]
                database = scanner.Scanner(database)
            if database:
                genres = self.getGenres(database)
                if getattr(self, 'associator', None):
                    taste = self.associator.getRating(genres)
                    # Based on rating
                    if nick == "stephen":
                        icon = 'terrific.png'
                    elif nick == "ruth":
                        icon = 'terrible.png'
                    elif nick == "peter":
                        icon = 'bad.png'
                    elif nick == "james":
                        icon = 'good.png'
                    elif nick == "nick":
                        icon = 'bad.png'
                else:
                    taste = "Unknown!"
                    icon = 'missingdata.png'

                total = len(database)
                colour = "black"
            else:
                taste = "Nothing submitted!"
                icon = 'missingdata.png'
                colour = "grey"

            if self.username == nick:
                self.model.append(
                        [gtk.gdk.pixbuf_new_from_file('img/me.png'), 
                            nick, total, "red", database, time])
            else:
                self.model.append([
                    gtk.gdk.pixbuf_new_from_file('img/%s' % icon), 
                    nick, total, colour, database, time])

    def updateStatus(self, text):
        statusbar = self.wTree.get_widget("statusbar")
        statusbar.push(statusbar.get_context_id("statusbar"), text)

class State:
    """This class represents the current state of the application"""

    __single = None

    def __init__(self):
        if State.__single:
            raise State.__single
        State.__single = self
        self.state = {
                'appstate' : 'idle',
                'connstate' : 'disconnected'
        }

    def isConnected(self):
        return self.state['connstate'] == 'connected'

    def isUpdating(self):
        return self.state['appstate'] == 'updating'

    def setConnected(self, connected):
        self.state['connstate'] = connected and 'connected' or 'disconnected'

    def setUpdating(self, updating):
        self.state['appstate'] = updating and 'updating' or 'idle'

parser = OptionParser(usage="%prog path", version="0.1",
        description="Scan music library")
options, args = parser.parse_args()

if len(args) < 1:
    parser.error("too few arguments")

if __name__ == "__main__":
    try:
        Interface = Interface()
        gtk.gdk.threads_init()
        gtk.main()
    except KeyboardInterrupt:
        print "Exiting.."
        sys.exit(0)

# vim: set expandtab shiftwidth=4 softtabstop=4 textwidth=79:
