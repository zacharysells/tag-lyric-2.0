#! /usr/bin/python

import argparse # Argument parsing library.
import sys # Used to call system.exit().
import os.path # Used to determine if files exist.
import eyed3 # mp3 file tagger


def tag_lyric(file):
    "Tags an mp3 file with lyrics. If an invalid file is passed, function will return -1"

    if ( not(os.path.isfile(file)) or not(file.endswith('.mp3')) ):
        return -1

    print file

    return

parser = argparse.ArgumentParser()

parser.add_argument('-a', action="store_true", default=False,
help = "Include this argument if you want to manually embed the artist name in the mp3 file")

parser.add_argument('-t', action="store_true", default=False,
help = "Include this argument if you want to manually embed the title namee in the mp3 file")

parser.add_argument('mp3', nargs = '*', help = "Path to mp3 file you want tagged")

try:
    args = parser.parse_args()
    if(len(args.mp3) == 0):
        print "Nothing to do"
        exit(0)


    for file in args.mp3:
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
