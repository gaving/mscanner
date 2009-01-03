#! /usr/bin/env python

# Title: ID3v2 - Informal standard (at www.id3.org)
# http://www.id3.org/id3v2.3.0.html#secA
# http://en.wikipedia.org/wiki/List_of_subcultures

GROUPS = {

    "ACID" : [
        "Acid",
        "Acid Jazz",
        "Acid Punk"
    ],

    "DOWNBEAT" : [
        "Ballad",
        "Bass",
        "Bebob",
        "Big Band",
        "Blues",
        "Celtic",
        "Classical",
        "Country",
        "Jazz",
        "Jazz+Funk",
        "Lo-Fi",
        "National Folk",
        "Native American",
        "Oldies",
        "Slow Jam",
        "Sonata",
        "Swing"
        "Tango",
    ],

    "DANCE" : [
        "Club",
        "Dance",
        "Dance Hall"
        "Disco",
        "Eurodance",
        "Euro-House",
        "Euro-Techno",
        "House",
        "Latin",
        "Rave"
    ],

    "FOLK" : [
        "Folk",
        "Folklore",
        "Folk-Rock",
        "National Folk",
        "Pop-Folk",
    ],

    "GOTH" : [
        "Darkwave",
        "Death Metal",
        "Gothic",
        "Gothic Rock",
        "Grunge",
        "Hard Rock"
        "Industrial",
        "Metal",
        "Punk",
        "Techno",
        "Techno-Industrial",
        "Trance"
    ],

    "INDIE" : [
        "Alternative",
        "AlternRock",
        "Folk",
        "Folklore",
        "Folk-Rock",
        "Industrial",
        "Instrumental",
        "Instrumental Rock",
        "Punk Rock",
        "Rock",
        "Rock & Roll",
        "Trip-Hop"
    ],

    "SHOEGAZING" : [
        "Ambient",
        "Avantgarde",
        "Easy Listening",
        "Electronic",
        "Meditative",
        "Trip-Hop",
        "Psychadelic"
        "Symphony",
        "Tribal"
    ],

    "RAP" : [
        "A capella",
        "Christian Rap",
        "Freestyle",
        "Gangsta",
        "Gospel",
        "Hip-Hop",
        "Rap",
        "R&B",
        "Reggae",
        "Retro",
        "Revival",
        "Rhythmic Soul",
        "Soul"
    ],

    "ROCK" : [
        "AlternRock",
        "Classic Rock",
        "Folk-Rock",
        "Gothic Rock",
        "Hard Rock"
        "Instrumental Rock",
        "Progressive Rock",
        "Psychedelic Rock",
        "Punk Rock",
        "Rock",
        "Rock & Roll",
        "Slow Rock",
        "Southern Rock",
        "Symphonic Rock"
    ],
        
    "POP" : [
        "Instrumental Pop",
        "Pop",
        "Pop-Folk",
        "Pop/Funk",
    ],

    "UNGROUPED" : [
        "Bluegrass",
        "Booty Bass",
        "Cabaret",
        "Chamber Music",
        "Chanson",
        "Cult",
        "Ethnic",
        "Fast Fusion",
        "Funk",
        "Fusion",
        "Game",
        "Jungle",
        "New Age",
        "New Wave",
        "Noise",
        "Polka",
        "Power Ballad",
        "Primus",
        "Samba",
        "Showtunes",
        "Ska",
        "Soundtrack",
        "Space",
    ],

    # Genres by definition that are "Unknown"
    "UNKNOWN" : [
        "Other"
    ],

    # Strange, rare genres
    "WEIRD" : [
        "Acoustic",
        "Chorus",
        "Comedy",
        "Dream",
        "Drum Solo",
        "Duet",
        "Humour",
        "Musical",
        "Opera",
        "Porn Groove",
        "Pranks",
        "Satire"
        "Sound Clip",
        "Speech",
        "Top 40",
        "Trailer",
        "Vocal",
    ]

} 

class Associator:

    def __init__(self, database):
        self.database = database
        print "Obtained local genres : %d" % len(database)

    def breakDown(self, profile=None):
        if not profile:
            profile = self.database
        genre_count = float(len(profile))
        groups = {}
        for genre, percent, count in profile:
            for label, genres in GROUPS.items():
                if genre in genres:
                    if groups.has_key(label):
                        groups[label] = groups[label] + 1
                    else:
                        groups[label] = 1
                else:
                    if groups.has_key("UNMATCHED"):
                        groups["UNMATCHED"] = groups["UNMATCHED"] + 1
                    else:
                        groups["UNMATCHED"] = 1

        print "Comparing local with %d genres to remote with %d" % (len(self.database), 
                len(profile))

        return groups

# vim: set expandtab shiftwidth=4 softtabstop=4 textwidth=79:
