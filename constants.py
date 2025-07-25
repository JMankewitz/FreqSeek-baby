## This file is part of PyGaze - the open-source toolbox for eye tracking

# SUBJECT PATHING
LOGFILEPATH = 'eyetrackingData/' #set path for eyetracking data
print(LOGFILEPATH)
LOGFILENAME = LOGFILEPATH #initialize file name
LOGFILE = LOGFILENAME # .txt; adding path before logfilename is optional; logs responses (NOT eye movements, these are stored in an EDF file!)

DUMMYMODE = True # False for gaze contingent display, True for dummy mode (using mouse or joystick)
# general
TRACKERTYPE = 'dummy' # either 'smi', 'eyelink' or 'dummy' (NB: if DUMMYMODE is True, trackertype will be set to dummy automatically)
#TRACKERTYPE = 'tobii'

# DISPLAY
# used in libscreen, for the *_display functions. The values may be adjusted,
# but not the constant's names
SCREENNR = 1 # number of the screen used for displaying experiment
DISPTYPE = 'psychopy' # either 'psychopy' or 'pygame'
DISPSIZE = (1920, 1080) # canvas size
#SCREENSIZE = (34.5, 19.7) # physical display size in cm
MOUSEVISIBLE = True # mouse visibility
#BGC = (125,125,125) # backgroundcolour
BGC = "black" # backgroundcolour
FGC = "black" # foregroundcolour

# SOUND
# defaults used in libsound. The values may be adjusted, but not the constants'
# names
SOUNDOSCILLATOR = 'sine' # 'sine', 'saw', 'square' or 'whitenoise'
SOUNDFREQUENCY = 440 # Herz
SOUNDLENGTH = 100 # milliseconds (duration)
SOUNDATTACK = 0 # milliseconds (fade-in)
SOUNDDECAY = 5 # milliseconds (fade-out)
SOUNDBUFFERSIZE = 1024 # increase if playback is choppy
SOUNDSAMPLINGFREQUENCY = 44100 # samples per second
SOUNDSAMPLESIZE = -16 # determines bit depth (negative is signed
SOUNDCHANNELS = 2 # 1 = mono, 2 = stereo

# INPUT
# used in libinput. The values may be adjusted, but not the constant names.
MOUSEBUTTONLIST = None # None for all mouse buttons; list of numbers for buttons of choice (e.g. [1,3] for buttons 1 and 3)
MOUSETIMEOUT = None # None for no timeout, or a value in milliseconds
KEYLIST = ['space', 'enter', 'left', 'right', 'z'] # None for all keys; list of keynames for keys of choice (e.g. ['space','9',':'] for space, 9 and ; keys)
KEYTIMEOUT = 1 # None for no timeout, or a value in milliseconds
JOYBUTTONLIST = None # None for all joystick buttons; list of button numbers (start counting at 0) for buttons of choice (e.g. [0,3] for buttons 0 and 3 - may be reffered to as 1 and 4 in other programs)
JOYTIMEOUT = None # None for no timeout, or a value in milliseconds


# EYETRACKER

SACCVELTHRESH = 35 # degrees per second, saccade velocity threshold
SACCACCTHRESH = 9500 # degrees per second, saccade acceleration threshold
EVENTDETECTION = 'native'
# EyeLink only
# SMI only
SMIIP = '127.0.0.1'
SMISENDPORT = 4444
SMIRECEIVEPORT = 5555

# FRL
# Used in libgazecon.FRL. The values may be adjusted, but not the constant names.
FRLSIZE = 200 # pixles, FRL-size
FRLDIST = 125 # distance between fixation point and FRL
FRLTYPE = 'gauss' # 'circle', 'gauss', 'ramp' or 'raisedCosine'
FRLPOS = 'center' # 'center', 'top', 'topright', 'right', 'bottomright', 'bottom', 'bottomleft', 'left', or 'topleft'

# CURSOR
# Used in libgazecon.Cursor. The values may be adjusted, but not the constants' names
CURSORTYPE = 'cross' # 'rectangle', 'ellipse', 'plus' (+), 'cross' (X), 'arrow'
CURSORSIZE = 20 # pixels, either an integer value or a tuple for width and height (w,h)
CURSORCOLOUR = 'pink' # colour name (e.g. 'red'), a tuple RGB-triplet (e.g. (255, 255, 255) for white or (0,0,0) for black), or a RGBA-value (e.g. (255,0,0,255) for red)
CURSORFILL = True # True for filled cursor, False for non filled cursor
CURSORPENWIDTH = 3 # cursor edge width in pixels (only if cursor is not filled)
