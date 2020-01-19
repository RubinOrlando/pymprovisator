#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
# Pymprovisator v. 0.1.1
# This program is free software. See the files LICENSE.TXT and README.TXT for more details
# Written by David Asorey Álvarez (forodejazz@yahoo.es). Madrid (Spain). August 2003.

from constants import *
from chord import *
from bass import BassLine
from drums import DrumsLine
from piano import PianoLine

class Style:
    def __init__(self, name, meter, tempo_unit):
        self.name = name
        self.meter = meter
        self.tempo_unit = tempo_unit


# Now, we set a few styles
even_eights = Style('even_eights', '4/4', '4')
# RO:add if not hidden elsewhere: even_sixteens = Style('even_sixteens', '4/4', '4')
latin1 = Style('latin1', '4/4', '4')
latin2 = Style('latin2', '4/4', '4')
bossa = Style('bossa', '4/4', '4')
samba1 = Style('samba1', '4/4', '4')
samba2 = Style('samba2', '4/4', '4')
ballad = Style('ballad', '4/4', '4')
funk = Style('funk', '4/4', '4')
rock = Style('rock', '4/4', '4')
basic = Style('basic', '4/4', '4') # RO: find out: is this jazz? or else? What are the specifics?

available_styles = [even_eights, latin1, latin2, bossa, samba1, samba2, ballad, funk, rock, basic] # RO:add even_sixteens ? (l22)

class Song:
    """This class represents a song. The parameters are:
    id: String, without spaces. Used for file names
    title, tempo: Integer
    style: Style, as defined in class Style, n_choruses: Integer
    chord_seq: List of chords, each one prepended by its duration, ex.: ['4C7', '2Dm7', '2G7alt', '4Cm7', '4F7', '8Bbmaj7#11']
    instruments: List of instruments to be generated.
    """
    def __init__(self, id, title, tempo, key, style, chord_seq, n_bars, n_choruses, instruments):
        parts = 0
        if not key in valid_keys:
            raise MyException("Key %s not valid!" % key)
        self.id = id
        self.title = title
        self.tempo = tempo
        self.key = key
        self.style = style
        self.n_choruses = n_choruses
        self.n_bars = n_bars
        self.instruments = instruments
        self.chord_seq = chord_seq
        self.chord_item_collection = []
        if len(chord_seq) == 1: 
            self.chord_item_collection.append(ChordItem(chord_seq[0], prev=None, next=None))
        else:
            self.chord_item_collection.append(ChordItem(chord_seq[0], prev=None, next=chord_seq[1])) #First chord
            for x in range(1,len(chord_seq)-1): #Middle chords
                self.chord_item_collection.append(ChordItem(chord_seq[x], prev=chord_seq[x-1], next=chord_seq[x+1]))
            self.chord_item_collection.append(ChordItem(chord_seq[-1], prev=chord_seq[-2], next=None)) #Last chord
        for ci in self.chord_item_collection:
            parts += int(ci.parts)
        if parts != int(style.meter[0])*int(n_bars):
            raise MyException("Inconsistent parts and chords")

    def generate_song(self, prefered_instruments={'bass': 'Acoustic Bass', 'piano': 'Acoustic Grand Piano'}):
        """ prefered_instruments: Dictionary with the prefered MIDI instruments, ex.: {'bass': 'Acoustic Bass', 'piano': 'Acoustic Grand Piano'}
        """
        temp = generate_song_header(self.title, self.style.meter, self.style.tempo_unit, self.tempo, self.key)
        self.bass_line = BassLine(prefered_instruments['bass'])
        self.piano_line = PianoLine(prefered_instruments['piano'])
        self.drums_line = DrumsLine()
        if 'bass' in self.instruments: temp += self.bass_line.generate_line(self)
        if 'piano' in self.instruments: temp += self.piano_line.generate_line(self)
        if 'drums' in self.instruments: temp += self.drums_line.generate_line(self)
        return temp

if __name__ == '__main__':
    example_input = ['4CM', '4DM', '4EM', '2FM', '2GM',
                    '4CM', '4DM', '4EM', '2FM', '2GM',
                    '4CM', '4BM', '2AM', '2GM', '2FM', '1EM', '1DM']
    s = Song( 'test', 'Test Song', '120', 'Eb', basic, example_input, '12', '3', ['bass', 'piano', 'drums'])
    prefered_instruments = {'bass': 'Acoustic Bass', 'piano': 'Acoustic Grand Piano'}
    import preferences
    final = s.generate_song(preferences.get_prefered_instruments())
    abc_file = open('basic.abc', 'w')
    for l in final:
        abc_file.write(l + "\n")
    abc_file.close()
    import os
    os.system('abc2midi basic.abc -o basic.mid')
