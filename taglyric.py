#! /usr/bin/python

import argparse # Argument parsing library.
import sys # Used to call system.exit().
import os.path # Used to determine if files exist.
import eyed3 # mp3 file tagger

import urllib2 # used to make http requests to lyric databases

import re

def lyrics_url(e_file):
    url =  "lyrics.com/"
    title = e_file.tag.title
    title = title.encode('ascii', 'ignore')

    artist = e_file.tag.artist
    artist = artist.encode('ascii', 'ignore')

    url = url                           \
        + re.sub(' ', '-', title)       \
        + "-lyrics-"                    \
        + re.sub(' ', '-', artist)      \
        + ".html"

    print url

def azlyrics_url(e_file):
    url = "azlyrics.com"

    print url

lyricDatabases = {0 : lyrics_url,
                  1 : azlyrics_url}


def generate_lyrics(file):
    "Generates a lyric url. Searches through each of the available databases until lyrics are found"

    e_file = eyed3.load(file)
    for i in lyricDatabases:
        url = lyricDatabases[i](e_file)


def is_mp3_file(file):
    "Returns true if file argument is an mp3 file that exists in the current system. False otherwise"
    return (os.path.isfile(file)) and (file.endswith('.mp3'))

def tag_lyric(file):
    "Tags the file specified in the argument with lyrics. If an invalid file is passed, function will return -1"
    if not(is_mp3_file(file)):
        return -1

    lyrics = generate_lyrics(file)
    #file = urllib2.urlopen(lyric_url)
    #data = file.read()
    #file.close()

    #print data

    return

def tag_artist(file):
    "Tags the file specified in the argument with the artist. If an invalid file is passed, function will return -1"
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

parser = argparse.ArgumentParser()

parser.add_argument('-a', action="store_true", default=False,
help = "Include this argument if you want to manually embed the artist name in the mp3 file")

parser.add_argument('-t', action="store_true", default=False,
help = "Include this argument if you want to manually embed the title name in the mp3 file")

parser.add_argument('-p', action="store_true", default=False,
help = "Include this argument if you want to see a print out of each files current tags")

parser.add_argument('mp3', nargs = '*', help = "Path to mp3 file you want tagged")

try:
    args = parser.parse_args()
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
