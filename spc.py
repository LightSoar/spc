""" 
Python script to decode a Thermo Grams *.SPC file format base
@author: Rohan Isaac

Notes
-----
+ Used format specificiton [1]
+ Loads entire file into memory

To be implemented
-----------------
- Multiple data sets
- Independent x-data
- Old data format

References
----------
[1] Galactic Universal Data Format Specification 9/4/97, SPC.H
http://ftirsearch.com/features/converters/SPCFileFormat.htm
"""

# need to functionalize 
from __future__ import division
import struct
import numpy as np 
import binascii as ba
import matplotlib.pyplot as plt

# could remove soon
def meta(**kwargs):
    for name, value in kwargs.items():
        print name,value
        
# write better version, perhaps include in main code upate docs on top
def flag_bits(n):
    """Return the bits of a byte as a boolean array:
    
    n (charater):
        8-bit character passed
    
    Returns
    -------    
    list (bool):
        boolean list representing the bits in the byte
        (big endian) ['most sig bit', ... , 'least sig bit' ]
        
    Example
    -------
    >>> flag_bits('A') # ASCII 65, Binary: 01000001
    [False, True, False, False, False, False, False, True]
    """
    return [x == '1' for x in list('{0:08b}'.format(ord(n)))]   

# load file (pass as argc) !!!
# need to modularize the whole thing anyways
with open("Data/nir.spc", "rb") as file:
#with open("HENE27.SPC", "rb") as file:
    content = file.read()
    
#--------------------------
# unpack header
#--------------------------

"""
 header string format (c: char, i: int, d: double, f:float, 
 10s: 10 character string; sizes: 1,4,8,4,10 respectively )
 
 use little-endian format with standard sizes 
 (hopefully doesn't vary across platforms, should check)
"""

format_str = "<cccciddicccci9s9sh32s130s30siicchf48sfifc187s"
# if need to check size of above string
# struct.calcsize(format_str)

# byte positon of various parts of the file
HEAD_POS = 512
SUBHEAD_POS = 544
    
# Unpack header (using naming scheme in SPC.H header file)
ftflg, fversn, fexper, fexp, fnpts, ffirst, flast, fnsub, \
    fxtype, fytype, fztype, fpost, fdate, fres, fsource, fpeakpt, \
    fspare, fcmnt, fcatxt, flogoff, fmods, fprocs, flevel, fsampin, ffactor, \
    fmethod, fzinc, fwplanes, fwinc, fwtype, freserv \
    = struct.unpack(format_str, content[:HEAD_POS])
    
    
#--------------------------
# Flag bits
#--------------------------
    
[tsprec, tcgram, tmulti, trandm, tordrd, talabs, txyxys, txvals] = flag_bits(ftflg)[::-1]

if tsprec:
    print "16-bit y data"
if tcgram:
    print "enable fexper"
if tmulti:
    print "multiple traces"
if trandm:
    print "arb time (z) values"
if tordrd:
    print "ordered but uneven subtimes"
if talabs:
    print "use fcatxt axis not fxtype"
if txyxys:
    print "each subfile has own x's"
if txvals:
    print "floating x-value array preceeds y's"

#--------------------------
# spc format version
#--------------------------

if fversn == ba.unhexlify('4b'):
    print "new LSB 1st"
elif fversn == ba.unhexlify('4c'):
    print "new MSB 1st"
elif fversn == ba.unhexlify('4d'):
    print "old format (unsupported)"
    
    # beginnings of an implementation
    old_format_str = "<ccifffccicccc8sii28s130s30s32s"
    print struct.calcsize(old_format_str)
else:
    print "unknown version"
    
#--------------------------
# experiment type
#--------------------------
fexper_op = ["General SPC", "Gas Chromatogram", "General Chromatogram", \
     "HPLC Chromatogram", "FT-IR, FT-NIR, FT-Raman Spectrum or Igram",\
     "NIR Spectrum", "UV-VIS Spectrum", "X-ray Diffraction Spectrum", \
     "Mass Spectrum ", "NMR Spectrum or FID", "Raman Spectrum",\
     "Fluorescence Spectrum", "Atomic Spectrum", \
     "Chromatography Diode Array Spectra"]
     
EXP_TYPE = fexper_op[ord(fexper)]
print EXP_TYPE

#--------------------------
# subfiles or not
#--------------------------
SUBFILES = int(fnsub)
if SUBFILES == 1:
    print "Single file only" 
else:
    print "Multiple subfiles"
    
#--------------------------
# units for x,z,w axes
#--------------------------
fxtype_op = ["Arbitrary", "Wavenumber (cm-1)", "Micrometers (um)", \
     "Nanometers (nm)", "Seconds ", "Minutes", "Hertz (Hz)", \
     "Kilohertz (KHz)", "Megahertz (MHz) ", "Mass (M/z)", \
     "Parts per million (PPM)", "Days", "Years", "Raman Shift (cm-1)", \
     "eV", "XYZ text labels in fcatxt (old 0x4D version only)", \
     "Diode Number", "Channel", "Degrees", "Temperature (F)",  \
     "Temperature (C)", "Temperature (K)", "Data Points", \
     "Milliseconds (mSec)", "Microseconds (uSec) ", "Nanoseconds (nSec)", \
     "Gigahertz (GHz)", "Centimeters (cm)", "Meters (m)", \
     "Millimeters (mm)", "Hours"]
     
fxtype_ord = ord(fxtype)
if fxtype_ord < 30:
    xlabel = fxtype_op[fxtype_ord]
else:
    xlabel = "Unknown"

    
#--------------------------
# units y-axis
#--------------------------

fytype_op = ["Arbitrary Intensity", "Interferogram", "Absorbance", \
    "Kubelka-Monk", "Counts", "Volts", "Degrees", "Milliamps", "Millimeters", \
    "Millivolts", "Log(1/R)", "Percent", "Intensity", "Relative Intensity", \
    "Energy", "", "Decibel","", "", "Temperature (F)", "Temperature (C)", \
    "Temperature (K)", "Index of Refraction [N]", "Extinction Coeff. [K]", \
    "Real", "Imaginary", "Complex"]

fytype_op2 = ["Transmission", "Reflectance", \
    "Arbitrary or Single Beam with Valley Peaks",  "Emission" ]

fytype_ord = ord(fytype)
if fytype_ord < 27:
    ylabel = fytype_op[fytype_ord]
elif fytype > 127 and fytype_ord < 132:
    ylabel = fytype_op2[fytype_ord - 128]
else:
    ylabel = "Unknown"    
     
#--------------------------
# spacing between data
#--------------------------
PTS = int(fnpts)
FIRST = int(ffirst)
LAST = int(flast)
SPACING = (LAST-FIRST)/(PTS-1)
print "There are ", PTS, " points between ", FIRST, " and ", LAST, " in steps of ", SPACING 

#--------------------------
# file comment
#--------------------------
# only need the first part of the string. some test files seem that there
# is junk after that
print str(fcmnt).split('\x00')[0]

#--------------------------
# loop over files
#--------------------------

for i in range(SUBFILES):
    print i


#--------------------------
# decode subheader
#--------------------------

subheader_str = "<cchfffiif4s"
print "Size of sub", struct.calcsize(subheader_str)
subflgs, subexp, subindx, subtime, subnext, \
    subnois, subnpts, subscan, subwlevel, subresv \
    = struct.unpack(subheader_str, content[HEAD_POS:HEAD_POS+32])
    
# do stuff if subflgs
    # if 1 subfile changed
    # if 8 if peak table should not be used
    # if 128 if subfile modified by arithmetic

#--------------------------
# decode x,y-data
#--------------------------

# header + subheader + mumber of data points (int: 4 bytes)
# ONLY VALID FOR SINGLE SUBFILES !!! need to fix
DATA_POS = 512 + 32 + (PTS*4)
EXP = ord(fexp)
PTS = int(fnpts)

# generate x-values (np.arange can't generate the correct amount of elements)
x_values = np.zeros(PTS)
for i in range(PTS):
    x_values[i] = ffirst + (SPACING*i)
    
# import the y-data and convert it
y_int = np.array(struct.unpack("i"*PTS,content[SUBHEAD_POS:DATA_POS]))

# conversion string
y_values = (2**(EXP-32))*y_int

# optionally integerize it
y_values_int = y_values.astype(int)
    

#--------------------------
# find column headers
#--------------------------    

if talabs:
    # if supposed to use fcatxt, split it based on 00 string and only use the 
    # first elements to get the x and y labels
    [xl, yl] =  fcatxt.split('\x00')[:2]
else:
    [xl, yl] = [xlabel,ylabel]
print xl, "\t", yl
for i in range(PTS):
    print x_values[i], "\t", y_values_int[i]
    #, y_values[i]
    continue


# plot the results
plt.plot(x_values,y_values)
plt.xlabel(xl)
plt.ylabel(yl)

# Optional metadata, check if it exists first 
metastr = '[SCAN PARAM]\r\n'
metapos = content.find(metastr)
if metapos != -1:
    metadata = content[metapos+len(metastr):]
    metalst = metadata.split('\r\n')
    keylst = []
    vallst = []
    for x in metalst[1:-1]:
        [key,val] = x.split('=')
        keylst.append(key)
        vallst.append(val)
        continue
    
    metadict = dict(zip(keylst,vallst))
    
    output = ['Comment','Start','End', 'Increment', 'Integration Time']
    print "Scan: ", metadict['Comment']
    print float(metadict['Start']), "to ", \
        float(metadict['End']), "; ", \
        float(metadict['Increment']), "cm-1;", \
        float(metadict['Integration Time']), "s integration time"