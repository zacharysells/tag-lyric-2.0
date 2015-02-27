#! /usr/bin/python

import argparse # Argument parsing library.
import sys # Used to call system.exit().
import os
import os.path # Used to determine if files exist.
import eyed3 # DEPENDENCY mp3 file tagger
from eyed3.id3 import ID3_V1_0, ID3_V1_1, ID3_V2_3, ID3_V2_4

import urllib # used to make http requests to lyric databases
import httplib # HTTPerror exception
import re # regular expression library used to strip strings
from bs4 import BeautifulSoup # DEPENDENCY. Need to install beautiful soup package. Used for html parsing

eyed3.log.setLevel("ERROR")

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# TODO add log level warnings
class loglevel:
    FATAL = bcolors.FAIL
    WARN = bcolors.WARNING

def lyrics_url(e_file):
    "Generates url for this lyric website returns None is title or artist are empty"

    url =  "http://www.lyrics.com/"

    title = e_file.tag.title
    artist = e_file.tag.artist

    if not title or not artist:
        return None

    title = title.encode('ascii', 'ignore')
    title = re.sub('[()\']', '', title)
    artist = artist.encode('ascii', 'ignore')

    url = url                           \
        + re.sub(r'\W+', '-', title)    \
        + "-lyrics-"                    \
        + re.sub(r'\W+', '-', artist)   \
        + ".html"

    return url

def lyrics_getLyrics(e_file):
    "Retrieves lyrics from the 'url' argument. Returns None \
    if the song or lyric was not found on the site"
    url = lyrics_url(e_file)
    if url is None:
        return None
    try:
        webpage = urllib.urlopen(url)

    except(IOError, httplib.HTTPException):
        # TODO
        #log("http response exception caught", loglevel.WARN)
        return None

    html = webpage.read()
    soup = BeautifulSoup(html)

    # Search for lyrics div
    lyrics = soup.find(id="lyric_space")

    # If lyrics div is not present in html, we know that the song does exist on this site
    if(lyrics is None):
        return None

    # Song exists on this site.
    else:
        lyrics = lyrics.get_text()

        # If stripped "lyric" text is too short, song does not have a lyric record on this site.
        if(len(lyrics) < 200):
            return None

        else:
            return lyrics


def azlyrics_url(e_file):
    "Generates url for this lyric website. Returns None if title or artist are empty"

    url = "http://www.azlyrics.com/lyrics/"

    title = e_file.tag.title
    artist = e_file.tag.artist
    if not title or not artist:
        return None

    title = title.encode('ascii', 'ignore')
    title = title.lower()
    artist = artist.encode('ascii', 'ignore')
    artist = artist.lower()

    # Strip non alphanumeric characters from title and artist strings.
    url = url                           \
        + re.sub(r'\W+', '', artist)    \
        + "/"                           \
        + re.sub(r'\W+', '', title)     \
        + ".html"

    return url

def azlyrics_getLyrics(e_file):
    "Retrieves lyrics from the 'url' argument. MUST return None \
    if the song or lyric was not found on the site"
    url = azlyrics_url(e_file)
    if url is None:
        return None
    try:
        webpage = urllib.urlopen(url)

    except (IOError, httplib.HTTPException):
        # TODO
        #log("http response exception caught", loglevel.WARN)
        return None

    html = webpage.read()
    soup = BeautifulSoup(html)
    # There should only be one div with the style attribute set in the following way.
    lyrics = soup.find('div', {"style" : "margin-left:10px;margin-right:10px;"})

    # If no div matches the above attribute, lyrics do no exits on site.
    if(lyrics is None):
        return None
    else:
        lyrics = lyrics.get_text()
        return lyrics


# Lyric site list
lyricDatabases = {0 : lyrics_getLyrics,
                  1 : azlyrics_getLyrics}


def generate_lyrics(file):
    "Generates a lyric url. Searches through each of the available databases \
    until lyrics are found"

    e_file = eyed3.load(file)
    for i in lyricDatabases:
        lyrics = lyricDatabases[i](e_file)
        if(lyrics is not None):
            return lyrics
    return None


def is_mp3_file(file):
    "Returns true if file argument is an mp3 file that exists in the current \
    system. False otherwise"
    return (os.path.isfile(file)) and (file.endswith('.mp3'))


def tag_lyric(file):
    "Tags the file specified in the argument with lyrics. If an invalid file \
    is passed, function will return -1"
    tag_lyric.count += 1
    print("(%d/%d)" % (tag_lyric.count ,nfiles)),
    if not(is_mp3_file(file)):
        print bcolors.FAIL + "Invalid file: " + bcolors.ENDC + file
        return -1

    lyrics = generate_lyrics(file)
    if(lyrics is None):
        # TODO turn this into log
        print bcolors.FAIL + "No lyrics found for: " + bcolors.ENDC + file
        return -1

    else:
        # TODO turn this into log
        print bcolors.OKGREEN + "Lyrics found for: " + bcolors.ENDC + file
        e_file = eyed3.load(file)
        e_file.tag.lyrics.set(lyrics)

        e_file.tag.save(file, version=ID3_V2_3)

    return
tag_lyric.count = 0

def recursive_tag_lyric(folder):
    "Calls recursive_tag_lyric recursively on a directory and it's subdirectories"

    for dirpath, dirnames, filenames in os.walk(folder):
        for dir in dirnames:
            recursive_tag_lyric(dir)
        for file in filenames:
            tag_lyric(os.path.join(dirpath,file))

def tag_artist(file, artist):
    "Tags the file specified in the argument with the artist. If an invalid \
    file is passed, function will return -1"
    if not(is_mp3_file(file)):
        return -1

    e_file = eyed3.load(file)
    e_file.tag.artist = unicode(artist, "UTF-8")
    e_file.tag.save()

def tag_title(file, title):
    "Tags the file specified in the argument with the title. If an invalid \
    file is passed, function will return -1"
    if not(is_mp3_file(file)):
        return -1

    e_file = eyed3.load(file)
    e_file.tag.title = unicode(title, "UTF-8")
    e_file.tag.save()

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
    'test.mp3' existing in ./test_songs/test.mp3"

    if not(os.path.isfile("test_songs/test.mp3")):
         print "Please make sure the file 'test.mp3' exists in the current", \
         "working directory and is a valid mp3 file"
         exit(0)

    print "mp3 Title: ",
    title = raw_input()
    print "mp3 Artist: ",
    artist = raw_input()

    e_file = eyed3.load("test_songs/test.mp3")
    # Strings must be converted to unicode before eyed3 will process them
    # even though we encode back to ascii in the url functions. This is okay
    # since this method will only be called during testing.
    e_file.tag.title = unicode(title, "UTF-8")
    e_file.tag.artist = unicode(artist, "UTF-8")

    e_file.tag.save()

    for i in lyricDatabases:
        url = lyricDatabases[i](e_file)
        print lyricDatabases[i].__name__, ": ", url

def count_file_args(args):
    "Counts all files passed by recursively searching through subdirectories"
    count = 0
    for file in args:
        if os.path.isfile(file):
            count += 1
        else:
            count += sum([len(files) for r, d, files in os.walk(file)])

    return count

parser = argparse.ArgumentParser()

parser.add_argument('-p', action="store_true", default=False,
help = "Print each files current tags")

parser.add_argument('-u', action="store_true", default=False,
help = "Print generated URLs for each file. Used for debugging")

parser.add_argument('--test', action="store_true", default=False,
help = "Prompts for title and artist. Print lyrics from each database given the title and artist")

parser.add_argument('-a', default=False, nargs=2,
help = "Embed the artist name in the mp3 file")

parser.add_argument('-t', default=False, nargs=2,
help = "Embed the title name in the mp3 file")

parser.add_argument('mp3', nargs = '*',
help = "Path to mp3 file you want tagged")

try:
    args = parser.parse_args()

    if (args.test):
        test_lyric_urls()
        exit(0)

    if (args.a):
        tag_artist(args.a[0], args.a[1])
        exit(0)

    if (args.t):
        tag_title(args.t[0], args.t[1])
        exit(0)

    if(len(args.mp3) == 0):
        print "Nothing to do"
        exit(0)

    nfiles = count_file_args(args.mp3)
    for file in args.mp3:

        if (args.p):
            print_tags(file)
            continue
        #if (args.u):
            # TODO
            # print_url(file)

        if(os.path.isdir(file)):
            recursive_tag_lyric(file)

        else:
            tag_lyric(file)

except IOError, msg:
    parser.error(str(msg))
