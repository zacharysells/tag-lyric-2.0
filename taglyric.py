#! /usr/bin/python

import argparse # Argument parsing library.
import sys # Used to call system.exit().
import os.path # Used to determine if files exist.
import eyed3 # mp3 file tagger

import urllib2 # used to make http requests to lyric databases
import re # regular expression library used to strip strings

def lyrics_url(e_file):
    url =  "lyrics.com/"

    # Remove any non ascii characters from the title and artist strings.
    title = e_file.tag.title
    title = title.encode('ascii', 'ignore')
    title = re.sub('[()]', '', title)

    artist = e_file.tag.artist
    artist = artist.encode('ascii', 'ignore')

    url = url                           \
        + re.sub(r'\W+', '-', title)       \
        + "-lyrics-"                    \
        + re.sub(r'\W+', '-', artist)      \
        + ".html"

    return url

def azlyrics_url(e_file):
    url = "azlyrics.com/lyrics/"

    # Remove any non ascii characters from title and artist strings.
    title = e_file.tag.title
    title = title.encode('ascii', 'ignore')
    title = title.lower()

    artist = e_file.tag.artist
    artist = artist.encode('ascii', 'ignore')
    artist = artist.lower()

    # Strip non alphanumeric characters from title and artist strings.
    url = url                           \
        + re.sub(r'\W+', '', artist)    \
        + "/"                           \
        + re.sub(r'\W+', '', title)     \
        + ".html"

    return url

lyricDatabases = {0 : lyrics_url,
                  1 : azlyrics_url}


def generate_lyrics(file):
    "Generates a lyric url. Searches through each of the available databases \
    until lyrics are found"

    e_file = eyed3.load(file)
    for i in lyricDatabases:
        url = lyricDatabases[i](e_file)


def is_mp3_file(file):
    "Returns true if file argument is an mp3 file that exists in the current \
    system. False otherwise"
    return (os.path.isfile(file)) and (file.endswith('.mp3'))

def tag_lyric(file):
    "Tags the file specified in the argument with lyrics. If an invalid file \
    is passed, function will return -1"
    if not(is_mp3_file(file)):
        return -1

    lyrics = generate_lyrics(file)
    #file = urllib2.urlopen(lyric_url)
    #data = file.read()
    #file.close()

    #print data

    return

def tag_artist(file):
    "Tags the file specified in the argument with the artist. If an invalid \
    file is passed, function will return -1"
    if not(is_mp3_file(file)):
        return -1

    e_file = eyed3.load(file)
    print "Song artist: ", e_file.tag.artist

def tag_title(file):

    if not(is_mp3_file(file)):
        return -1

    e_file = eyed3.load(file)
    print "Song title: ", e_file.tag.title

def print_tags(file):

    if not(is_mp3_file(file)):
        return -1

    e_file = eyed3.load(file)

    # Add color to these text outputs source: http://stackoverflow.com/questions/287871/print-in-terminal-with-colors-using-python
    print "-----------------------------------------"
    print "Filename: ", os.path.basename(file)
    print "Song title: ", e_file.tag.title
    print "Song artist: ", e_file.tag.artist
    print "-----------------------------------------"

def test_lyric_urls():
    "This method prints the url formatting of each database with the title \
    and artist strings from stdin. This method relies on the mp3 file       \
    'test.mp3' existing in the current working directory"

    if not(os.path.isfile("test.mp3")):
         print "Please make sure the file 'test.mp3' exists in the current", \
         "working directory and is a valid mp3 file"
         exit(0)

    print "mp3 Title: ",
    title = raw_input()
    print "mp3 Artist: ",
    artist = raw_input()

    e_file = eyed3.load("test.mp3")
    # Strings must be converted to unicode before eyed3 will process them
    # even though we encode back to ascii in the url functions. This is okay
    # since this method will only be called during testing.
    e_file.tag.title = unicode(title, "UTF-8")
    e_file.tag.artist = unicode(artist, "UTF-8")

    e_file.tag.save()

    for i in lyricDatabases:
        url = lyricDatabases[i](e_file)
        print lyricDatabases[i].__name__, ": ", url

parser = argparse.ArgumentParser()

parser.add_argument('-a', action="store_true", default=False,
help = "Include this argument if you want to manually embed the artist name in the mp3 file")

parser.add_argument('-t', action="store_true", default=False,
help = "Include this argument if you want to manually embed the title name in the mp3 file")

parser.add_argument('-p', action="store_true", default=False,
help = "Include this argument if you want to see a print out of each files current tags")

parser.add_argument('--test', action="store_true", default=False)

parser.add_argument('mp3', nargs = '*', help = "Path to mp3 file you want tagged")

try:
    args = parser.parse_args()

    if (args.test):
        test_lyric_urls()
        exit(0)

    if(len(args.mp3) == 0):
        print "Nothing to do"
        exit(0)


    for file in args.mp3:
        if (args.a):
            tag_artist(file)
        if (args.t):
            tag_title(file)
        if (args.p):
            print_tags(file)


        tag_lyric(file)



    #print audiofile.tag.title

except IOError, msg:
    parser.error(str(msg))
#print args.mp3

#for mp3file in args["mp3 file"]:
#    audiofile = eyed3.load(mp3file)
#    title = audiofile.tag.title
#    artist =  audiofile.tag.artist
#    audiofile.tag.lyrics.set(u"""la la la""")
#    audiofile.tag.save()
