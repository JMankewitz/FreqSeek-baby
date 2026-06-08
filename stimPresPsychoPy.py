############################
#  Import various modules  #
############################
import numpy
import glob, os, random, sys, gc, time

try:
	import winsound

	winSoundLoaded = True
except ImportError:
	print("Warning: winsound can't be imported. Will try to use pyo")
	winSoundLoaded = False
from math import *

try:
	import pygame
	from pygame.locals import *
except ImportError:
	print("Warning: pygame not found; will be using pyglet for stim presentation")

from psychopy import visual, core, event, data, info, prefs


def pollMouse():
	pass


# (x,y) = pygame.mouse.get_pos()
# y = self.experiment.screen.size[1]-y # convert to OpenGL coords
# return [x,y]


def pollMouseCorrected():
	pass


# maxY = self.experiment.screen.size[1]
# (x,y) = pygame.mouse.get_pos()
# y = maxY-y # convert to OpenGL coords
# return [x,y]

def newTextureObject(win, image, position=[0, 0]):
	return visual.SimpleImageStim(win, image=image, units='', pos=position)


def newText(win, text, pos=[0, 0], color="gray", scale=1.0):
	if win.units == "pix":
		height = 30 * scale
		wrapWidth = int(win.size[0] * .8)
	else:  # assumes degree
		height = .7 * scale
		wrapWidth = 30
	return visual.TextStim(win, text=text, pos=pos, color=color, units=win.units, ori=0, height=height)


def randomButNot(arr, index):
	randIndex = index
	while randIndex == index:
		randIndex = random.randint(0, len(arr) - 1)
	return arr[randIndex]


def polarToRect(angleList, radius):
	coords = []
	for curAngle in angleList:
		radAngle = (float(curAngle) * 2.0 * pi) / 360.0
		xCoord = round(float(radius) * cos(radAngle), 0)
		yCoord = round(float(radius) * sin(radAngle), 0)
		coords.append([xCoord, yCoord])
	return coords


def calculateRectangularCoordinates(distanceX, distanceY, numCols, numRows):
	coord = [[0, 0]] * numCols * numRows
	curObj = 0
	for curCol in range(0, numCols):  # x-coord
		for curRow in range(0, numRows):  # y-coord
			coord[curObj] = (curCol * distanceX, curRow * distanceY)
			curObj = curObj + 1
	xCorrect = max(map(lambda x: x[0], coord)) / 2
	yCorrect = max(map(lambda x: x[1], coord)) / 2
	return map(lambda x: [x[0] - xCorrect, x[1] - yCorrect], coord)


def setAndPresentStimulus(win, stimuli, duration=0):
	"""Stimuli can be a list or a single draw-able stimulus"""
	if type(stimuli).__name__ == "list":
		for curStim in stimuli:
			curStim.draw()
	else:
		stimuli.draw()
	if duration == 0:  # single frame
		win.flip()
	else:
		win.flip()
		core.wait(duration)
	return


def setPresentAndWaitForEnter(win, stimuli, inputDevice='keyboard'):
	"""Stimuli can be a list or a single draw-able stimulus"""
	if type(stimuli).__name__ == "list":
		for curStim in stimuli:
			curStim.draw()
	else:
		stimuli.draw()
	win.flip()
	if inputDevice == "keyboard":
		global event
		event.waitKeys(keyList=['return', 'enter'])
	elif inputDevice == "gamepad" or inputDevice == "mouse":
		while True:
			for event in pygame.event.get():  # check responses
				if inputDevice == 'mouse':
					if event.type == pygame.MOUSEBUTTONDOWN:
						pygame.event.clear()
						return
				if event.type == pygame.KEYDOWN or event.type == pygame.JOYBUTTONDOWN:
					pygame.event.clear()
					return


def moveMouseCursor(self, win, startX, startY):
	mouse1 = mouse2 = mouse3 = 0
	self.mouseCursor.setPos([startX, startY])
	while True:
		mouse1, mouse2, mouse3 = self.myMouse.getPressed()
		if (mouse1):
			moved = True
			self.mouseCursor.setPos(self.myMouse.getPos())
			mouse_dX, mouse_dY = self.myMouse.getPos()
			mouse_dX -= startX  # get position relative to the starting position
			mouse_dY -= startY
		self.targetRect.draw()
		self.mouseCursor.draw()
		win.flip()  # redraw the buffer


def newRect(win, size=[0, 0], pos=[0, 0], color="gray"):
	return visual.PatchStim(win, tex='None', texRes=1024, mask='None', color=color, size=size, pos=pos)


def playAndWait(sound, soundPath='', winSound=False, waitFor=-1):
	"""Sound (other than winSound) runs on a separate thread. Waitfor controls how long to pause before resuming. -1 for length of sound"""
	print("Audiolib:", prefs.hardware['audioLib'])

	if not winSoundLoaded:
		winSound = False
	if prefs.hardware['audioLib'] == ['pygame']:
		# default to using winsound
		winSound = True
	if winSound:
		print('using winsound to play sound')
		if waitFor != 0:
			winsound.PlaySound(sound, winsound.SND_MEMORY)
		else:  # playing asynchronously - need to load the path.
			if soundPath:
				winsound.PlaySound(soundPath, winsound.SND_FILENAME | winsound.SND_ASYNC)
			else:
				sys.exit("sound path not provided to playAndWait")
		return
	else:
		if waitFor < 0:
			waitDurationInSecs = sound.getDuration()
		elif waitFor > 0:
			waitDurationInSecs = waitFor
		else:
			waitDurationInSecs = 0

		if waitDurationInSecs > 0:
			sound.play()
			core.wait(waitDurationInSecs)
			sound.stop()
			return
		else:
			sound.play()
			# print('returning right away'
			return


def showText(win, textToShow, color=[-1, -1, -1], waitForKey=True, acceptOnly=0, inputDevice="keyboard", mouse=False,
			 pos=[0, 0], scale=1):
	global event
	# event.clearEvents() #clear all events just in case
	win.flip()
	if win.units == "pix":
		height = 30 * scale
		wrapWidth = int(win.size[0] * .8)
	elif win.units == "deg":
		height = .7 * scale
		wrapWidth = 30
	else:
		wrapWidth = None
	textStim = visual.TextStim(win, pos=pos, wrapWidth=wrapWidth, color=color, height=height, text=textToShow)
	textStim.draw()
	win.flip()
	if mouse:
		while any(mouse.getPressed()):
			core.wait(.1)  # waits for the user to release the mouse
		while not any(mouse.getPressed()):
			pass
		return
	elif inputDevice == "keyboard":
		if waitForKey:
			if acceptOnly == 0:
				event.waitKeys()
			else:
				# event.waitKeys(keyList=list(str(acceptOnly)))
				event.waitKeys(keyList=[acceptOnly])
			return
		else:
			# event.clearEvents(eventType='keyboard')
			return
	elif inputDevice == "gamepad":  # also uses mouse if mouse is not false
		while True:
			for event in pygame.event.get():  # check responses
				if mouse:
					if event.type == pygame.MOUSEBUTTONDOWN:
						pygame.event.clear()
						return
				if event.type == pygame.KEYDOWN or event.type == pygame.JOYBUTTONDOWN:
					pygame.event.clear()
					return


def waitingAnimation(win, size=20, distanceBetweenElements=3, numElements=8, delay=1.0):
	totalWidth = numElements * (size + distanceBetweenElements)
	positions = range(totalWidth / -2, totalWidth / 2, (size + distanceBetweenElements))
	for curFrame in range(numElements, -1, -1):
		for curElement in range(curFrame):
			visual.PatchStim(win, color='white', size=size, tex='None', mask='circle',
							 pos=[positions[curElement], 0]).draw()
		win.flip()
		core.wait(delay)


def playWinSound(soundPath):
	winsound.PlaySound(soundPath, winsound.SND_FILENAME | winsound.SND_ASYNC)


def giveFeedback(isRight):
	if isRight == 1:
		playWinSound('bleep')
	else:
		playWinSound('buzz')


class LoomAnimation:
    """
    Animation class that handles three phases of animation:
    1. Loom in (grow larger)
    2. Wiggle at large size
    3. Loom out (shrink back to original)
    
    Parameters:
    -----------
    stim : psychopy.visual.ImageStim
        The stimulus to animate
    win : psychopy.visual.Window
        The window to display the animation in
    pos : tuple or None
        The position of the stimulus in window coordinates (if None, uses current position)
    init_size : tuple or int or None
        Initial size of the stimulus (if None, uses current size)
    target_size_factor : float
        Factor to multiply the initial size by for target size (default: 1.5)
    init_opacity : float
        Initial opacity of the stimulus (default: 1.0)
    target_opacity : float
        Target opacity for looming phase (default: 1.0)
    loom_in_duration : float
        Duration of the loom in (growing) phase in seconds (default: 1.0)
    wiggle_duration : float
        Duration of the wiggling phase in seconds (default: 2.0)
    loom_out_duration : float
        Duration of the loom out (shrinking) phase in seconds (default: 1.0)
    jiggle_amplitude : float
        Maximum rotation angle in degrees (default: 5)
    jiggle_frequency : float
        Frequency of oscillation in Hz (default: 2)
    looping : bool
        Whether to loop the animation continuously (default: False)
    """
    # Define explicit states
    LOOMING_IN = "looming_in"     # Growing larger
    WIGGLING = "wiggling"         # Wiggling at large size
    LOOMING_OUT = "looming_out"   # Shrinking back
    COMPLETE = "complete"
    PAUSED = "paused"

    def __init__(self, stim, win, pos=None, 
                 init_size=None, target_size_factor=1.5,
                 init_opacity=1.0, target_opacity=1.0,
                 loom_in_duration=1.0, wiggle_duration=2.0, loom_out_duration=1.0,
                 jiggle_amplitude=5, jiggle_frequency=2,
                 looping=False):

        self.stim = stim
        self.win = win
        self.looping = looping
        
        # Set position if provided
        if pos is not None:
            self.stim.pos = pos
        self.pos = self.stim.pos
        
        # Initialize sizes
        self.init_size = init_size if init_size is not None else stim.size
        if isinstance(self.init_size, (int, float)):
            self.init_size = (self.init_size, self.init_size)
        
        # Calculate target size
        self.target_size = (
            self.init_size[0] * target_size_factor,
            self.init_size[1] * target_size_factor
        )
        
        # Other animation parameters
        self.init_opacity = init_opacity
        self.target_opacity = target_opacity
        self.loom_in_duration = loom_in_duration
        self.wiggle_duration = wiggle_duration
        self.loom_out_duration = loom_out_duration
        self.jiggle_amplitude = jiggle_amplitude
        self.jiggle_frequency = jiggle_frequency

        # Store the original stimulus properties
        self.original_size = stim.size
        self.original_opacity = stim.opacity
        self.original_ori = stim.ori

        # Animation state variables
        from psychopy import core
        self.start_time = core.getTime()
        self.phase_start_time = self.start_time
        self.elapsed_time = 0
        self.paused_time = 0
        self.state = self.LOOMING_IN  # Start with growing phase
        self.current_size = self.init_size
        self.current_opacity = self.init_opacity
        self.current_angle = 0
        self.is_paused = False
        self.completed_cycles = 0
        
        # Set initial stimulus properties
        self.stim.size = self.init_size
        self.stim.opacity = self.init_opacity
        self.stim.ori = 0

    def update(self, current_time=None):
        """
        Update the animation state based on elapsed time.

        Parameters:
        -----------
        current_time : float, optional
            Current time in seconds. If None, gets current time.

        Returns:
        --------
        bool
            True if the animation is complete and not looping, False otherwise
        """
        from psychopy import core
        import math

        if current_time is None:
            current_time = core.getTime()
            
        # If paused, just store the time and return
        if self.is_paused:
            return False
            
        # Calculate elapsed time accounting for pauses
        if self.paused_time > 0:
            # Adjust start time to account for the pause
            self.phase_start_time += self.paused_time
            self.paused_time = 0
            
        elapsed = current_time - self.phase_start_time
        self.elapsed_time = elapsed

        # PHASE 1: Looming in (growing larger)
        if self.state == self.LOOMING_IN:
            progress = min(1.0, elapsed / self.loom_in_duration)
            
            # Calculate size interpolation (growing)
            self.current_size = (
                self.init_size[0] + progress * (self.target_size[0] - self.init_size[0]),
                self.init_size[1] + progress * (self.target_size[1] - self.init_size[1])
            )
            
            # Calculate opacity interpolation
            self.current_opacity = self.init_opacity + progress * (self.target_opacity - self.init_opacity)
            
            # Calculate jiggle (start subtle)
            self.current_angle = (progress * self.jiggle_amplitude) * math.sin(2 * math.pi * self.jiggle_frequency * elapsed)
            
            # Apply to stimulus
            self.stim.size = self.current_size
            self.stim.opacity = self.current_opacity
            self.stim.ori = self.current_angle
            
            # Transition to wiggling phase when complete
            if progress >= 1.0:
                self.state = self.WIGGLING
                self.phase_start_time = current_time
                
        # PHASE 2: Wiggling (maintain large size with jiggle)
        elif self.state == self.WIGGLING:
            progress = min(1.0, elapsed / self.wiggle_duration)
            
            # Maintain the target size
            self.stim.size = self.target_size
            
            # Full jiggle at target size
            self.current_angle = self.jiggle_amplitude * math.sin(2 * math.pi * self.jiggle_frequency * elapsed)
            self.stim.ori = self.current_angle
            
            # Transition to looming out when wiggle phase complete
            if progress >= 1.0:
                self.state = self.LOOMING_OUT
                self.phase_start_time = current_time
                
        # PHASE 3: Looming out (shrinking back)
        elif self.state == self.LOOMING_OUT:
            progress = min(1.0, elapsed / self.loom_out_duration)
            
            # Calculate size interpolation (shrinking)
            self.current_size = (
                self.target_size[0] - progress * (self.target_size[0] - self.init_size[0]),
                self.target_size[1] - progress * (self.target_size[1] - self.init_size[1])
            )
            
            # Calculate opacity interpolation (if changing)
            self.current_opacity = self.target_opacity - progress * (self.target_opacity - self.init_opacity)
            
            # Calculate jiggle (reducing as we shrink)
            self.current_angle = ((1.0 - progress) * self.jiggle_amplitude) * math.sin(2 * math.pi * self.jiggle_frequency * elapsed)
            
            # Apply to stimulus
            self.stim.size = self.current_size
            self.stim.opacity = self.current_opacity
            self.stim.ori = self.current_angle
            
            # Check if animation is complete
            if progress >= 1.0:
                self.completed_cycles += 1
                
                # If looping is enabled, restart the animation
                if self.looping:
                    self.state = self.LOOMING_IN
                    self.phase_start_time = current_time
                    return False  # Not complete, will continue looping
                else:
                    # Not looping, so mark as complete and reset
                    self.state = self.COMPLETE
                    self.reset_stimulus()
                    return True  # Animation is complete

        # Draw the stimulus (this will be called by the main routine)
        self.draw()
        
        return False  # Animation not complete or is looping

    def pause(self):
        """Pause the animation, remembering current state"""
        if not self.is_paused:
            from psychopy import core
            self.is_paused = True
            self.pause_start_time = core.getTime()

    def resume(self):
        """Resume the animation from where it left off"""
        if self.is_paused:
            from psychopy import core
            self.is_paused = False
            self.paused_time = core.getTime() - self.pause_start_time

    def reset_stimulus(self):
        """Reset the stimulus to its initial state"""
        self.stim.size = self.init_size
        self.stim.opacity = self.init_opacity
        self.stim.ori = 0

    def restart(self):
        """Restart the animation from the beginning"""
        from psychopy import core
        self.start_time = core.getTime()
        self.phase_start_time = self.start_time
        self.state = self.LOOMING_IN
        self.is_paused = False
        self.paused_time = 0
        # Reset the stimulus to its initial state
        self.reset_stimulus()

    def draw(self):
        """Draw the current animation frame"""
        self.stim.draw()

    def is_complete(self):
        """Check if animation has completed"""
        return self.state == self.COMPLETE

    def get_completed_cycles(self):
        """Get the number of completed animation cycles"""
        return self.completed_cycles
    @property
    def is_running(self):
        """
        True when the animation is actively updating
        (i.e., not paused and not finished).
        """
        return (not self.is_paused) and (self.state != self.COMPLETE)
	

# utils for readability
AOI_NAMES = ["topLeft", "topRight", "bottomLeft", "bottomRight", "away", "none"]

class ActiveTrialController:
    """One controller instance per active trial."""
    FIXATION_MS = 300
    LABEL_MIN_MS = 1000
    LABEL_MAX_MS = 2500          # e.g. self.maxLabelTime
    LOOKAWAY_MS = 200            # awayThreshold / noneThreshold
	
    def __init__(self, owner, cur_trial):
        # --------------- handles -----------------
        self.owner  = owner                # ExpPresentation layer
        self.exp    = owner.experiment     # low‑level Experiment
        self.win    = self.exp.win
        self.tracker = self.exp.tracker

        self.posAOIS     = owner.posAOIS      # polygons for hit‑testing
        self.lookAwayPos = owner.lookAwayPos  # special “away” coordinate/value

        # --------------- trial / state -----------
        self.trial   = cur_trial
        self.state   = "IDLE"
        self.cur_aoi = None

        AOI_NAMES = ["topLeft", "topRight", "bottomLeft", "bottomRight",
                     "away", "none"]
        self.fix_clock   = {a: core.Clock() for a in AOI_NAMES}   # per‑AOI
        self.label_clock = core.Clock()                           # audio loop

        # --------------- assets ------------------
        self.assets = self._make_assets()

        # pause all animations until first selection
        for asset in self.assets.values():
            asset['anim'].pause()

    # ---------- helper construction ----------
    def _make_assets(self):
        """Return a mapping AOI → visuals/anim/audio."""
        assets = {}
        for aoi in ["topLeft", "topRight", "bottomLeft", "bottomRight"]:
            stim_name  = self.trial[f"{aoi}Stim"]
            label_name = self.trial[f"{aoi}Label"]

            stim_img   = self.owner.imageMatrix[stim_name][0]
            stim_img.pos  = self.owner.pos[aoi]
            stim_img.size = self.owner.stim_size

            assets[aoi] = dict(
                stim  = stim_img,
                rect  = visual.Rect(
                            self.win,
                            width=self.owner.fam_rect_size[0],
                            height=self.owner.fam_rect_size[1],
                            fillColor="lightgray",
                            pos=self.owner.pos[aoi]),
                anim  = LoomAnimation(
                            stim=stim_img,
                            win=self.win,
                            init_size=stim_img.size,
                            target_size_factor=self.owner.targetSizeFactor,
                            loom_in_duration=self.owner.loomDuration,
                            loom_out_duration=self.owner.loomDuration,
                            wiggle_duration=self.owner.wiggleDuration,
                            jiggle_amplitude=self.owner.jiggleAmplitude,
                            jiggle_frequency=self.owner.jiggleFrequency,
                            looping=True),
                audio = self.owner.soundMatrix[label_name],
            )
        return assets

    # ---------- main loop ----------
    def run(self, timeout_s):
        trial_clock = core.Clock()
        while trial_clock.getTime() < timeout_s:
            aoi = self._sample_aoi()
            self._update_state(aoi)
            self._draw()              # all drawing in one spot
            self.exp.win.flip()

    # ---------- gaze handling ----------
    def _sample_aoi(self):
        """Sample tracker, return AOI string."""
        gaze = self.tracker.sample()
        for aoi in AOI_NAMES[:4]:
            if self.posAOIS[aoi].contains(gaze):      # <-- now points to alias
             return aoi
        return "away" if gaze == self.lookAwayPos else "none"

    def _update_state(self, aoi):
        if self.state == "IDLE":
            self._idle_logic(aoi)
        elif self.state == "PLAYING":
            self._playing_logic(aoi)

    # ----- IDLE → PLAYING -----
    def _idle_logic(self, aoi):
        if aoi in AOI_NAMES[:4]:
            # start / continue fixation timer for this AOI
            if self.cur_aoi != aoi:
                self.fix_clock[aoi].reset()
                self.cur_aoi = aoi
            # if 300 ms reached → trigger
            if self.fix_clock[aoi].getTime() * 1000 >= self.FIXATION_MS:
                self._start_event(aoi)

    # ----- PLAYING state -----
    def _playing_logic(self, aoi):
        played_ms = self.label_clock.getTime() * 1000

        # conditions that *could* end the event
        hit_max_time     = played_ms >= self.LABEL_MAX_MS
        away_long_enough = (aoi in ["away", "none"] and
                            self.fix_clock[aoi].getTime()*1000 >= self.LOOKAWAY_MS)
        switched_object  = (aoi != self.cur_aoi and
                            aoi in AOI_NAMES[:4] and
                            self.fix_clock[aoi].getTime()*1000 >= self.FIXATION_MS)

        # We may end ONLY if we've reached the MIN duration
        can_end = played_ms >= self.LABEL_MIN_MS and (
                    hit_max_time or away_long_enough or switched_object)

        if can_end:
            self._end_event()
            if switched_object:          # immediate restart on new AOI
                self._start_event(aoi)
            return                       # done with this cycle

        # -- still playing: handle looping after MIN met --
        snd = self.assets[self.cur_aoi]['audio']
        if played_ms >= self.LABEL_MIN_MS and not snd.isPlaying:
            snd.stop()
            snd.play()
            self.label_clock.reset()

    # ---------- start / end helpers ----------
    def _start_event(self, aoi):
        # pause & reset EVERY animation
        for asset in self.assets.values():
            asset['anim'].pause()
            asset['anim'].reset_stimulus()

        # start chosen anim + audio
        anim = self.assets[aoi]['anim']
        snd  = self.assets[aoi]['audio']

        anim.resume()
        # --- KICK‑START: do NOT flip here; just mark that the next _draw must update ---
        self.first_frame = True             # add an attribute

        snd.stop()
        snd.play()
        self.label_clock.reset()

        self.state   = "PLAYING"
        self.cur_aoi = aoi
        if self.exp.subjVariables['eyetracker'] == "yes":
			# log event
            self.exp.tracker.log("startAudio")

    def _end_event(self):
        # stop anim/audio
        self.assets[self.cur_aoi]['anim'].pause()
        self.assets[self.cur_aoi]['audio'].stop()
        self.assets[self.cur_aoi]['anim'].reset_stimulus()

        if self.exp.subjVariables['eyetracker'] == "yes":
			# log event
            self.exp.tracker.log("endAudio")
        self.state   = "IDLE"
        self.cur_aoi = None
        # make sure fixation timers restart fresh
        for clk in self.fix_clock.values():
            clk.reset()

    # ---------- drawing ----------
    def _draw(self):
        # background rectangles
        for asset in self.assets.values():
            asset['rect'].draw()

        # if an event is running, draw its animation frame
        if self.state == "PLAYING":
            self.assets[self.cur_aoi]['anim'].update()   # draws loom frame

        # draw static images for *all* AOIs when IDLE,
        # and for *non‑active* AOIs when PLAYING
        for name, asset in self.assets.items():
            if self.state != "PLAYING" or name != self.cur_aoi:
                asset['stim'].draw()