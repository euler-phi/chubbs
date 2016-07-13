# chubbs

Dependencies: 

    rtl-sdr and librtlsdr-dev
Install with "sudo apt-get install rtl-sdr librtlsdr-dev". You ***MUST*** (read:
not optional) determine your specific SDR's PPM error, or this (and any other)
SDR application will not work properly. The standard method for doing this is to
run "rtl_test -p" for several minutes until your cumulative PPM value converges.
This is the value you will use with the -e flag when running chubbs.  The PPM
value for an SDR is unlikely to change over time, but will be different from
dongle to dongle. 


    aisdeco 
Available here: http://xdeco.org/?page_id=30 (I'm doing this on an RPi 3, so I
used an older version specifically for the Pi, AisDeco v.20140704, which worked
just fine for my purposes). If you're using some other Linux flavor and install
aisdeco2, you must either rename the binary to "aisdeco", or edit the two
strings in this file where aisdeco is called (change to aisdeco2). The former is
probably the easier method.

    libais 
Available here: https://github.com/schwehr/libais

    libxml2 and libxslt 
Needed for KML export. Install with "sudo apt-get install libxml2 libxslt-dev"

    pykml 
What we needed the two dependencies above for. If you have pip
(Python's package manager) already installed, install with "pip install pykml"
If you don't, then we'll need to first install pip with "sudo apt-get install
python-pip", then "pip install pykml".

Just add:

A decent antenna for the SDR (~162 MHz)

KML export: 

Often, it's helpful to be able to plot the vessels observed on your trip on
Google Earth/Maps.  You can do this by using the -k flag. Because a time stamp
is included, it is extra important that your system time be correct if using
this option.

Final remarks (really, I'll shut up after this):

It's not bulletproof; this is a quick proof-of-concept/demo that involved
just a couple hours of total work. Of note, there is some repetitiveness of
alerts, especially if verbosity is enabled. I recommend only triggering on
either the name or MMSI to avoid this in non-verbose mode, and of the two, MMSI
is probably the better method.  I've noticed a weird @ sign appended onto the
name of a buoy in Guam after like a dozen spaces, which was weird, and makes me
feel like MMSI is the more industrial grade method. Plus, let's face it, a lot
of ships have hard names to spell. When it breaks on you, or if you can't get it
off the ground to begin with, send me a message

Reminder:

You must determine your PPM value! UTC time will be used for KML, but
it depends on the system time, so it you must ensure that it is accurate
if exporting to KML!
