from ais import decode
from pykml.factory import KML_ElementMaker as KML
from lxml import etree
import socket
import subprocess
import sys
import argparse
import time
import datetime
import os

'''
Program: chubbs.py
Author: Erik Rye 
Date: 5 July 2016
Description: A simple wrapper around aisdeco and libais, AIS decoding programs,
that has the useful benefit of being able to *alert* you to particular vessels
of interest based on their MMSI or vessel name. 

Updated: 12 July 2016
Changelog: -k flag added for KML export. -fn and -fm flags added for passing
newline-separated vessel names and MMSIs, respectively, rather than typing a
list of 100s of vessel names and MMSIs into the shell.

Dependencies: 

    rtl-sdr and librtlsdr-dev --  Install with "sudo apt-get install rtl-sdr
    librtlsdr-dev". You ***MUST*** (read: not optional) determine your specific
    SDR's PPM error, or this (and any other) SDR application will not work
    properly. The standard method for doing this is to run "rtl_test -p" for
    several minutes until your cumulative PPM value converges. This is the value
    you will use with the -e flag when running chubbs. The PPM value for an SDR
    is unlikely to change over time, but will be different from dongle to
    dongle.

    aisdeco - available here: http://xdeco.org/?page_id=30
    (I'm doing this on an RPi 3, so I used an older version specifically for the
    Pi, AisDeco v.20140704, which worked just fine for my purposes). If you're
    using some other Linux flavor and install aisdeco2, you must either rename
    the binary to "aisdeco", or edit the two strings in this file where aisdeco
    is called (change to aisdeco2). The former is probably the easier method.

    libais - available here: https://github.com/schwehr/libais

    libxml2 and libxslt -- needed for KML export. Install with 
    "sudo apt-get install libxml2 libxslt-dev"

    pykml -- what we needed the two dependencies above for. If you have pip
    (Python's package manager) already installed, install with 
    "pip install pykml"
    If you don't, then we'll need to first install pip with
    "sudo apt-get install python-pip", then "pip install pykml".

Just add:
    A decent antenna for the SDR (~162 MHz)

KML export: 
    Often, it's helpful to be able to plot the vessels observed on your trip on
    Google Earth/Maps.  You can do this by using the -k flag. Because a time
    stamp is included, it is extra important that your system time be correct if
    using this option.

Final remarks (really, I'll shut up after this):
    It's not bulletproof; this is a quick proof-of-concept/demo that involved
    just a couple hours of total work. Of note, there is some repetitiveness of
    alerts, especially if verbosity is enabled. I recommend only triggering on
    either the name or MMSI to avoid this in non-verbose mode, and of the two,
    MMSI is probably the better method.  I've noticed a weird @ sign appended
    onto the name of a buoy in Guam after like a dozen spaces, which was weird,
    and makes me feel like MMSI is the more industrial grade method. Plus, let's
    face it, a lot of ships have hard names to spell. When it breaks on you, or
    if you can't get it off the ground to begin with, send me an email.

Reminder:
    You ***MUST*** determine your PPM value! UTC time will be used for KML, but
    it depends on the system time, so it you ***MUST*** ensure that it is
    accurate if exporting to KML!
'''

def print_welcome():
    '''
    It is what it is...
    '''
    wstr =(" _____  _   _ _   _____________  _____  \n"
           "/  __ \| | | | | | | ___ \ ___ \/  ___| \n"
           "| /  \/| |_| | | | | |_/ / |_/ /\ `--.  \n"
           "| |    |  _  | | | | ___ \ ___ \ `--. \ \n"
           "| \__/\| | | | |_| | |_/ / |_/ //\__/ / \n"
           " \____/\_| |_/\___/\____/\____/ \____/  \n")
    
    print "Welcome to..."
    print wstr
    print "" 
    print "" 
    time.sleep(2)
                                       

def start_aisdeco(port, error):
    '''
    Starts aisdeco on specified port and with proper ppm value for SDR (Highly,
    highly important. Will not work with a bad ppm value
    '''
    if error:
        cmd = ("./aisdeco --freq 161975000 --freq 162025000 --freq-correction " +
               str(error) + " --net " + str(port))
    else:
        cmd = ("./aisdeco --freq 161975000 --freq 162025000 --net " + str(port))
    FNULL = open(os.devnull, 'w')
    print "...AIS decoder starting..."
    subprocess.Popen(cmd.split(), stdout=FNULL, stderr=FNULL)
    time.sleep(2)
    print "...AIS decoder started..."
    return None

def alert(m):
    '''
    Prints a nice alert messages
    '''

    try:
        name = m['name']
        print "Vessel name:", name
    except:
        pass
    try:
        print "MMSI:", m['mmsi']
    except:
        pass
    try:
        x = str(m['x'])
        y = str(m['y'])
        print "Latitude:", y
        print "Longitude:", x
    except: 
        pass
    print ""

    return None

def addKML(m, f):
    try:
        mmsi = m['mmsi']
        x = str(m['x'])
        y = str(m['y'])
        pm = KML.Placemark(
                KML.name(str(mmsi)),
                KML.Point(
                    KML.coordinates(x + ',' +  y)
                ),
                KML.TimeStamp(
                    KML.when(getTime())
                ),
             )
        f.append(pm)
    except:    
        pass


def getTime():
    '''
    Returns an ISO formatted string with UTC time. This is based on the system
    time, so it is imperative that the system time is correct for the time zone
    you are in.
    '''
    return datetime.datetime.utcfromtimestamp(time.time()).isoformat()+'Z'

if __name__ == "__main__":
    print_welcome()
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--mmsi', 
                        help="MMSI(s) of a vessel or vessels of interest", 
                        type=int,
                        nargs="+")
    parser.add_argument('-n', '--name', 
                        help="Name(s) of a vessel or vessels of interest", 
                        type=str,
                        nargs="+")
    parser.add_argument('-p', '--port', 
                        help="Port to connect to aisdeco on (localhost)."
                        "Type: int, Default: 1369", 
                        type=int,
                        nargs="?",
                        default=1369)
    parser.add_argument('-e', '--error', 
                        help="SDR ppm error. Highly important! "
                        "If unsure, run 'rtl_test -p for several "
                        "minutes to obtain good ppm value. "
                        "Type: int, Default: 0",
                        type=int,
                        nargs="?",
                        default=0)
    parser.add_argument('-fm', '--mmsi_file', 
                        help="Name of file to read in newline-delimited "
                        "MMSIs (as opposed to typing them individually)."
                        "Type: str, Default: None",
                        type=str,
                        nargs="?",
                        default="")
    parser.add_argument('-fn', '--name_file', 
                        help="Name of file to read in newline-delimited "
                        "vessel names (as opposed to typing them "
                        "individually)."
                        "Type: str, Default: None",
                        type=str,
                        nargs="?",
                        default="")
    parser.add_argument("-k", "--kml", 
                        help="Writes KML w/all observed "
                        "vessels/aids to navigation. Object will "
                        "be named by its MMSI, with time stamp and lat/long "
                        "included. Time stamps will be UTC, but are generated "
                        "from system time, so it is very important "
                        "that this is accurate. Set to proper TZ.",
                        action="store_true")
    parser.add_argument("-v", "--verbose", 
                        help="Turn on verbosity. "
                        "Will display all AIS messages.",
                        action="store_true")

    print "Press ctrl-c to quit at any time."
    if not len(sys.argv) > 1:
        print "Usage: python chubbs.py [options]"
        print "Try 'python chubbs.py -h' for help"
        sys.exit()

    args = parser.parse_args()
    if args.mmsi:
        args.mmsi=set(args.mmsi)
    if args.name:
        args.name=set(args.name)
    if args.mmsi_file:
        if not args.mmsi:
            args.mmsi = set()
        with open(args.mmsi_file, 'r') as f:
            for line in f:
                mmsi = int(line.strip())
                args.mmsi.add(mmsi)
    if args.name_file:
        if not args.name:
            args.name= set()
        with open(args.name_file, 'r') as f:
            for line in f:
                name = line.strip()
                args.name.add(name)
    if args.mmsi:
        print "You're tracking the following MMSI(s):"
        for i in args.mmsi:
            print "MMSI:", i
        print ""
    if args.name:
        print "You're tracking the following name(s):"
        for i in args.name:
            print "Name:", i
        print ""
    if not (args.name or args.mmsi):
        print "You must either specify a name(s) or mmsi(s)"
        sys.exit()
    if args.kml:
        t = getTime()
        fname = '.'.join(t.split())+'.kml'
        fld = KML.Folder()


    start_aisdeco(args.port, args.error)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('localhost', args.port))
    while 1:
        try:
            line = s.recv(2048)
            line = line.strip()
            body = ''.join(line.split(',')[5])
            pad = int(line.split(',')[-1].split('*')[0][-1])
            try:
                msg = decode(body, pad)
                if args.verbose:
                    alert(msg)
                if args.kml:
                    addKML(msg,fld)
                try:
                    if args.mmsi and msg['mmsi'] in args.mmsi:
                        print "\n#########BEGIN ALERT#########\n"
                        alert(msg)
                        print "#########END ALERT#########\n"
                    if args.name and msg['name'] in args.name:
                        print "\n#########BEGIN ALERT#########"
                        alert(msg)
                        print "#########END ALERT#########\n"
                except KeyError:
                    pass
            #Hear no evil, see no evil, speak no evil
            except:
                pass
        except KeyboardInterrupt:
            with open(fname, 'w') as f:
                f.write(etree.tostring(fld, pretty_print=True))
            sys.exit()
