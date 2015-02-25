#! /usr/bin/python

import argparse # Argument parsing library.
import sys # Used to call system.exit().
import os.path # Used to determine if files exist.
import eyed3 # DEPENDENCY mp3 file tagger
from eyed3.id3 import ID3_V1_0, ID3_V1_1, ID3_V2_3, ID3_V2_4

import urllib # used to make http requests to lyric databases
import re # regular expression library used to strip strings
from bs4 import BeautifulSoup # DEPENDENCY. Need to install beautiful soup package. Used for html parsing

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def lyrics_url(e_file):
    url =  "http://www.lyrics.com/"

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

def lyrics_getLyrics(e_file):
    "Retrieves lyrics from the 'url' argument. MUST return None \
    if the song or lyric was not found on the site"
    url = lyrics_url(e_file)
    webpage = urllib.urlopen(url)
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
    url = "http://www.azlyrics.com/lyrics/"

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

def azlyrics_getLyrics(e_file):
    # TODO
    "Retrieves lyrics from the 'url' argument. MUST return None \
    if the song or lyric was not found on the site"
    url = azlyrics_url(e_file)
    webpage = urllib.urlopen(url)
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
lyricDatabases = {0 : azlyrics_getLyrics,
                  1 : lyrics_getLyrics}


def generate_lyrics(file):
    # TODO
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
    # TODO
    "Tags the file specified in the argument with lyrics. If an invalid file \
    is passed, function will return -1"
    if not(is_mp3_file(file)):
        return -1

    lyrics = generate_lyrics(file)
    if(lyrics is None):
        print bcolors.FAIL + "No lyrics found for: " + bcolors.ENDC + file
        return -1

    print bcolors.OKGREEN + "Lyrics found for: " + bcolors.ENDC + file
    e_file = eyed3.load(file)
    e_file.tag.lyrics.set(lyrics)

    e_file.tag.save(file, version=ID3_V2_3)

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

parser = argparse.ArgumentParser()

parser.add_argument('-a', action="store_true", default=False,
help = "Embed the artist name in the mp3 file")

parser.add_argument('-t', action="store_true", default=False,
help = "Embed the title name in the mp3 file")

parser.add_argument('-p', action="store_true", default=False,
help = "Print out of each files current tags")

parser.add_argument('--test', action="store_true", default=False,
help = "Prompts for title and artist. Print lyrics from each database given the title and artist")

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

except IOError, msg:
    parser.error(str(msg))
