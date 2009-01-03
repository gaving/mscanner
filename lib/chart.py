#! /usr/bin/env python

from pylab import *

class Chart:

    def makeChart(self, data):

        figure(1, figsize=(8,8))
        ax = axes([0.1, 0.1, 0.8, 0.8])

        labels = [x.replace('/', '') for x, y, z in data]
        fracs = [y for x, y, z in data]

#        explode=(0, 0.05, 0, 0)
        pie(fracs, labels=labels, autopct='%1.1f%%', shadow=True)
        title('Genre breakdown of music', bbox={'facecolor':0.8, 'pad':5})
        show()

# vim: set expandtab shiftwidth=4 softtabstop=4 textwidth=79:
