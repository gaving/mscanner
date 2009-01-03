#! /usr/bin/env python

import os
import pprint
import pickle

import gtk

import ID3
import mad

class Scanner:
    """This class represents the scanner"""

    class Track:
        """This class represents a single track in the database"""

        def __init__(self, artist="", title="", album="", genre="", length="", path=""):
            self.artist = artist
            self.title = title
            self.album = album
            self.genre = genre
            self.length = length
            self.path = path

        def fractSec(self, s):
            min, s = divmod(s, 60)
            return "%02d:%02d" % (min, s)

        def getLength(self):
            return self.length

        def getList(self):
            return {'artist' : self.artist, 'title' : self.title, 'album' :
                    self.album, 'genre' : self.genre}

        def __repr__(self):
            return "%s - %s - %s (%s)" % (self.artist, self.title, self.album,
                    self.genre)

    def __init__(self, list=None):
        self.db = []
        
        if list:
            for track in list:
                self.db.append(self.Track(
                    track['artist'], 
                    track['title'], 
                    track['album'], 
                    track['genre']))

    def __len__(self):
        return len(self.db)

    def add(self, fullpath):
        if not fullpath.endswith("mp3"):
            return
        print "** Processing %s" % fullpath
        try:
            meta = {}
            tag = ID3.ID3(fullpath)
            for key, val in tag.items():
                if val != None: 
                    meta[key] = val

            mf = mad.MadFile(fullpath)
            meta['LENGTH'] = mf.total_time() / 1000

            artist = meta['ARTIST']
            title = meta['TITLE']
            album = meta['ALBUM']
            genre = meta['GENRE']
            length = meta['LENGTH']
            self.db.append(self.Track(artist, title, album, genre, length, fullpath))
        except ID3.InvalidTagError:
            print "*** Problem reading tag, ignoring.."
            return
        except KeyError:
            print "*** Tag missing, ignoring.."
            return

    def clear(self):
        self.db = []

    def dumpDatabase(self, db=None):
        if db:
            pickle.dump(db, open(DATA_FILE, 'wb'))
        else:
            pickle.dump(self.db, open(DATA_FILE, 'wb'))

    def loadDatabase(self, file):
        pprint.pprint(pickle.load(open(file, 'rb')))

    def getGenres(self):
        genres = {}
        for track in self.db:
            track = track.getList()
            genre = track['genre']
            if genres.has_key(genre):
                genres[genre] = genres[genre] + 1
            else:
                genres[genre] = 1

        return genres

    def scan(self, path, scan_cb=None):
        print "* Opening %s" % path
        stack = [path]
        files = []
        while stack:
            directory = stack.pop()
            for file in os.listdir(directory):
                fullpath = os.path.join(directory, file)
                self.add(fullpath)
                if scan_cb:
                    scan_cb(fullpath)
                while gtk.events_pending():
                    gtk.main_iteration(False)
                if os.path.isdir(fullpath) and not os.path.islink(fullpath):
                    stack.append(fullpath)

    def toList(self):
        return [track.getList() for track in self.db]

    def organise(self):
        db = {}
        for song in self.db:
            try:
                song = song.getList()
                artist = song['artist']
                album = song['album']
                title = song['title']
                genre = song['genre']

                track = { 
                        'title' : title, 
                        'genre' : genre,
                }

                if db.has_key(artist):
                    if db[artist].has_key(album):
                        db[artist][album].append(track)
                    else:
                        db[artist][album] = []
                        db[artist][album].append(track)
                else:
                    db[artist] = {}
            except KeyError, e:
                print e

#        pprint.pprint(db)
        return db

    def view(self):
        for track in self.db:
            print track.getList()


# vim: set expandtab shiftwidth=4 softtabstop=4 textwidth=79:
