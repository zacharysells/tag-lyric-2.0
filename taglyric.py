#!/usr/bin/env python

"""
MP3 Tagger
"""

import sys
import re
import time
import readline
import os
import os.path
import xml.etree.cElementTree as et

import requests
import eyed3
eyed3.log.setLevel("ERROR")
from eyed3.id3 import ID3_V2_4
from colorama import Fore, Style


class LogLevel(object):  # pylint: disable=too-few-public-methods
    """
    Class containing log level strings
    """

    ERROR = "fatal"
    WARNING = "warning"
    NOTICE = "notice"
    GOOD = "good"

class TaggerConfig(object):  # pylint: disable=too-few-public-methods
    """
    Tagger support class to hold configuration values.
    """

    ARTISTS_LIB = "lib/artists.txt"
    TITLES_LIB = "lib/titles.txt"

    SLEEP_DUR = 0.2  # Time to sleep after making a request to avoid reset of connection
    IS_TAGGED_STRING = "MP3 Tagged"

class Tagger(object):
    """
    Main Tagger class that contains all main methods
    """

    def __init__(self):
        self.search_lyric_direct_uri = "http://api.chartlyrics.com/apiv1.asmx/SearchLyricDirect"
        self.search_lyric_uri = "http://api.chartlyrics.com/apiv1.asmx/SearchLyric"
        self.get_lyric_uri = "http://api.chartlyrics.com/apiv1.asmx/GetLyric"

        # Cached Artists and Titles for tab completing
        self.artist_completer = Completer(TaggerConfig.ARTISTS_LIB)
        self.title_completer = Completer(TaggerConfig.TITLES_LIB)

        self.namespace = {
            'chartlyrics': "http://api.chartlyrics.com/"
        }

    def _ensure_artist_title(self, e_file):
        """
        Ensure that the e_file that was passed in has a title and an artist tagged.
        If not, the user will be prompted for each empty field. The user's input is
        converted to title case before being tagged onto the file.

        Args:
            e_file: eyed3.mp3.Mp3AudioFile - File to ensure artist and title tags
        """

        if not e_file.tag:
            e_file.initTag(ID3_V2_4)

        title = e_file.tag.title
        artist = e_file.tag.artist
        if not title:
            log("[%s] No title tag associated with this file." % os.path.basename(e_file.path), LogLevel.WARNING)
            readline.parse_and_bind("tab: complete")
            readline.set_completer(self.title_completer.complete)
            title = raw_input("Enter a title: ")
            readline.set_completer()  # Reset the tab completing
            self.title_completer.add(title.title())
            # We're tagging the mp3 file after "title-ing" the inputed strings
            e_file.tag.title = unicode(title.title(), "UTF-8")

        if not artist:
            log("[%s] No artist tag associated with this file." % os.path.basename(e_file.path), LogLevel.WARNING)
            readline.parse_and_bind("tab: complete")
            readline.set_completer(self.artist_completer.complete)
            artist = raw_input("Enter an artist: ")
            readline.set_completer()  # Reset the tab completing

            self.artist_completer.add(artist.title())
            # We're tagging the mp3 file after "title-ing" the inputed strings
            e_file.tag.artist = unicode(artist.title(), "UTF-8")

        e_file.tag.save()

    def _search(self, title, artist):
        params = {
            "artist": artist,
            "song": title,
        }
        response = requests.get(self.search_lyric_uri, params=params)
        time.sleep(TaggerConfig.SLEEP_DUR)
        response = re.sub(' xmlns="[^"]+"', '', response.text, count=1)  # Remove the namespace
        root_xml = et.fromstring(response)

        # Parse the XML response into a dictionary
        key_mapping = {
            "Song": "title",
            "Artist": "artist",
            "LyricChecksum": "checksum",
            "LyricId": "id",
        }
        songs = []
        for lyric_result in root_xml:
            song = {}
            for track in lyric_result:
                if key_mapping.get(track.tag):
                    song.update({
                        key_mapping[track.tag]: track.text
                    })
            if song:
                songs.append(song)
        return songs

    def _search_lyric_direct(self, title, artist):
        params = {
            "artist": artist,
            "song": title,
        }
        response = requests.get(self.search_lyric_direct_uri, params=params)
        root_xml = et.fromstring(response.text.encode('utf-8'))
        lyrics = root_xml.find("chartlyrics:Lyric", self.namespace)
        time.sleep(TaggerConfig.SLEEP_DUR)
        return lyrics.text

    def _get_lyric(self, lyric_id, checksum):
        params = {
            "lyricId": lyric_id,
            "lyricCheckSum": checksum,
        }

        response = requests.get(self.get_lyric_uri, params=params)
        root_xml = et.fromstring(response.text.encode('utf-8'))
        lyrics = root_xml.find("chartlyrics:Lyric", self.namespace)
        time.sleep(TaggerConfig.SLEEP_DUR)
        return lyrics.text

    @staticmethod
    def _tag_lyrics(e_file, lyrics, tagged_status="1"):
        """
        Tag the given eyed3.mp3 file with the given lyrics. Sets it's tagged status appropriately.
        Args:
            e_file: eyed3.mp3.Mp3AudioFile - File to tag
            lyrics: lyrics to tag to the file
            tagged_status:
                "0" - Lyrics were not found or they were found and user chose to not tag the file
                "1" - Lyrics were found and tagged onto the file successfully.
        """

        e_file.tag.lyrics.set(unicode(lyrics))
        e_file.tag.user_text_frames.set(unicode(tagged_status), description=unicode(TaggerConfig.IS_TAGGED_STRING))


    def _is_tagged(self, e_file, lyrics):
        lyrics_curr = "".join([i.text for i in e_file.tag.lyrics])
        is_tagged = e_file.tag.user_text_frames.get(unicode(TaggerConfig.IS_TAGGED_STRING))
        if is_tagged:
            is_tagged = is_tagged.text

        # See if we already successfully tagged this file
        if lyrics_curr == lyrics or is_tagged == "1":
            log("[%s] Already tagged." % os.path.basename(e_file.path), LogLevel.GOOD)
            return True
        # See if we already tried to tag this file
        elif is_tagged == "0":
            log("[%s] Previously searched." % os.path.basename(e_file.path), LogLevel.WARNING)
            return True

        # If no lyrics are found, skip.
        elif not lyrics:
            self._tag_lyrics(e_file, "", tagged_status="0")
            log("[%s] No lyrics found" % os.path.basename(e_file.path), LogLevel.ERROR)
            return True

        else:
            return False

    def _tag(self, e_file, force=False):

        title = e_file.tag.title
        artist = e_file.tag.artist

        lyrics = self._search_lyric_direct(title, artist)
        if not force and self._is_tagged(e_file, lyrics):
            return

        print "%s\n...\n" % lyrics[:150]
        confirm = raw_input("\nDoes this look right[Y/n]? ") or "Y"
        if confirm.lower() == "y":
            self._tag_lyrics(e_file, lyrics, tagged_status="1")
            log("[%s] Done." % os.path.basename(e_file.path), LogLevel.GOOD)
        else:
            songs = self._search(e_file.tag.title, e_file.tag.artist)
            num_songs = 0
            for song in songs:
                if "id" not in song or "checksum" not in song:
                    continue
                num_songs += 1
                print "%d)" % (num_songs)
                print "Title: %s" % song["title"]
                print "Artist: %s" % song["artist"]
                print "Lyrics: "
                lyrics = self._get_lyric(song["id"], song["checksum"])
                print "%s\n...\n" % lyrics[:150]
                print "======================"
            choices = ["none"] + [str(i) for i in range(1, num_songs + 1)]
            track = get_choice("Which song matches? Enter \"none\" to skip: ", choices)
            if track == "none":
                # We're tagging the file's lyrics here with empty string to prevent re-prompting when
                # re-running this file.
                self. _tag_lyrics(e_file, "", tagged_status="0")
                log("[%s] Skipping." % os.path.basename(e_file.path), LogLevel.WARNING)
                return
            selection = songs[int(track) - 1]
            lyrics = self._get_lyric(selection["id"], selection["checksum"])
            self._tag_lyrics(e_file, lyrics, tagged_status="1")
            log("[%s] Done." % os.path.basename(e_file.path), LogLevel.GOOD)

    def get(self, args):
        """
        usage: mp3 get <TITLE>:<ARTIST>

        Attempt to download an mp3 file
        """
        pass

    def tag(self, args):
        """
        usage: mp3 tag [file1.mp3, file2.mp3, ...]

        Tag an mp3 file with lyrics.
        """

        for i, filename in enumerate(args):
            if not is_mp3_file(filename):
                log("(%d/%d) [%s] This isnt an mp3 file" %
                    (i + 1, len(args), os.path.basename(filename)), LogLevel.ERROR)
                continue

            e_file = eyed3.load(filename)
            self._ensure_artist_title(e_file)
            log("(%d/%d) [%s] Searching for lyrics..." %
                (i + 1, len(args), os.path.basename(filename)), LogLevel.NOTICE)
            self._tag(e_file, force="force" in args)
            e_file.tag.save(filename, version=ID3_V2_4)
            print

def log(msg, level):
    """
    Creates log string composed of date and message and writes it to stdout
    """

    log_level_mapping = {
        LogLevel.ERROR: Fore.RED,
        LogLevel.WARNING: Fore.YELLOW,
        LogLevel.NOTICE: Fore.BLUE,
        LogLevel.GOOD: Fore.GREEN,
    }

    date = time.strftime("%m-%d-%Y")
    print log_level_mapping[level] + date + " - " + msg, Style.RESET_ALL

def is_mp3_file(filepath):
    "Returns true if file argument is an mp3 file that exists in the current \
    system. False otherwise"
    return (os.path.isfile(filepath)) and (filepath.endswith('.mp3'))

def count_file_args(args):
    """
    Counts all files passed by recursively searching through subdirectories
    """

    count = 0
    for filename in args:
        if os.path.isfile(filename):
            count += 1
        else:
            count += sum([len(files) for _, _, files in os.walk(filename)])

    return count

def get_choice(prompt, responses):
    """
    Prompt the user until a valid response is entered
    """

    while True:
        response = raw_input(prompt)
        if response in responses:
            return response
        else:
            print "Invalid choice. Try again."

class Completer(object):
    """
    Class to support tab completion in the readline library_file
    """

    def __init__(self, library_file):
        self.library_file = library_file
        self.matches = []


        if not os.path.exists(library_file):
            open(library_file, 'w+')
        with open(library_file, 'r') as filep:
            options = filep.read().split('\n')
        self.options = sorted(options)

    def add(self, option):
        """
        Add an auto complete option to the Completer
        """

        if option not in self.options:
            self.options.append(option)

        with open(self.library_file, 'w') as filep:
            filep.write("\n".join(self.options))

    def complete(self, text, state):
        """
        Check if the input text matches an option in self.options
        This function is meant to be called by the readline module
        """

        if state == 0:
            if text:
                self.matches = [s for s in self.options if text in s]
            else:
                self.matches = self.options[:]

        try:
            return self.matches[state]
        except IndexError:
            return None

def print_help():
    """
    Print help text
    """

    print """usage mp3 COMMAND <args>

    Available commands:

    {:10s}Download an mp3 file
    {:10s}Tag an mp3 file
    {:10s}Print this help menu

    For help on any individual command, type mp3 COMMAND --help
    """.format("get", "tag", "help")

def main():
    """
    Main entrypoint into mp3 executable
    """

    tagger = Tagger()
    function_mapping = {
        "get": tagger.get,
        "tag": tagger.tag,
    }

    if len(sys.argv) < 2:
        print_help()
        return

    cmd = sys.argv[1]

    try:
        function_mapping[cmd](sys.argv[2:])
    except KeyError:
        print_help()

if __name__ == "__main__":
    main()
