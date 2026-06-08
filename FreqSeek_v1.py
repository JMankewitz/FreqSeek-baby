
# load pygaze libraries and custom pygaze libraries
import pygaze
from pygaze import libscreen, libinput, eyetracker, libtime
from pygaze.plugins import aoi
from stimPresPyGaze import *

# import constants for pygaze
import constants
import tobii_research as tr

# load psychopy and custom psychopy libraries
from baseDefsPsychoPy import *
from stimPresPsychoPy import *
from psychopy.hardware import keyboard
from psychopy import logging

logging.console.setLevel(logging.CRITICAL)

# load other utility functions
import csv
import os
import random

class Exp:
	def __init__(self):
		self.expName = "FreqSeek"
		self.path = os.getcwd()
		self.subjInfo = {
			'1': {'name': 'subjCode',
				  'prompt': 'EXP_XXX',
				  'options': 'any',
				  'default': self.expName + '_001'},
			'2': {'name': 'sex',
				  'prompt': 'Subject sex m/f: ',
				  'options': ("m","f"),
				  'default': '',
				  'type' : str},
			'3' : {	'name' : 'age',
					   'prompt' : 'Subject Age: ',
					   'options' : 'any',
					   'default':'',
					   'type' : str},
			'4': {'name': 'order',
                   'prompt': '(test / 1 / 2 / 3 / 4)',
                   'options': ("test", "1", "2", "3", "4"),
                   'default': "test",
                   'type': str},
			'5' : {'name' : 'expInitials',
				   'prompt' : 'Experimenter Initials: ',
				   'options' : 'any',
				   'default' : '',
				   'type' : str},
			'6': {	'name' : 'mainMonitor',
					  'prompt' : 'Screen Index (0,1,2,3): ',
					  'options' : (0,1,2,3),
					  'default': 2,
					  'type' : int},
			'7': {	'name' : 'sideMonitor',
					  'prompt' : 'Screen Index (0,1,2,3): ',
					  'options' : (0,1,2,3),
					  'default': 1,
					  'type' : int},
			'8': {'name': 'eyetracker',
                   'prompt': '(yes / no)',
                   'options': ("yes", "no"),
                   'default': "yes",
                   'type': str},
			'9': {'name': 'activeMode',
				  'prompt': 'input / gaze',
				  'options': ("input", "gaze"),
				  'default': "input",
				  'type': str},
			'10': {'name': 'responseDevice',
				  'prompt': 'keyboard / mouse',
				  'options': ("keyboard", "mouse"),
				  'default': 'keyboard'}
		}

		optionsReceived = False
		fileOpened = False

		# open data files to save while checking to make sure that no data is overwritten
		while not fileOpened:
			[optionsReceived, self.subjVariables] = enterSubjInfo(self.expName, self.subjInfo)
			print(self.subjVariables)

			from pygaze import settings
			print(constants.LOGFILE)
			settings.LOGFILE = constants.LOGFILEPATH + self.subjVariables['subjCode']
			print("settings logfile: " + settings.LOGFILE)

			print("Tracker type: " + constants.TRACKERTYPE)
			if not optionsReceived:
				popupError(self.subjVariables)

			elif not os.path.isfile('data/training/' + 'tracking_data_' + self.subjVariables['subjCode'] + '.txt'):

				# if using an eyetracker
				if self.subjVariables['eyetracker'] == "yes":
					# import eyetracking package from pygaze
					from pygaze import eyetracker

					if not os.path.isfile(settings.LOGFILE + '_TOBII_output.tsv'):
						fileOpened = True
						self.activeTrainingOutputFile = open(
							'data/activeTraining/' + 'tracking_data_' + self.subjVariables['subjCode'] + '.txt', 'w')

						self.trainingOutputFile = open('data/training/' + 'tracking_data_' + self.subjVariables['subjCode'] + '.txt',
												   'w')
						self. activeOutputFile = open(
							'data/' + 'activeTest/tracking_data_' + self.subjVariables['subjCode'] + '.txt',
							'w')

					else:
						fileOpened = False
						popupError(
							'That subject code for the eyetracking data already exists! The prompt will now close!')
						core.quit()
				else:
					#if eyetracker is no, only track the training output
					fileOpened = True
					self.trainingOutputFile = open(
						'data/training/' + 'tracking_data_' + self.subjVariables['subjCode'] + '.txt', 'w')

			else:
				fileOpened = False
				popupError('That subject code already exists!')

		self.disp = libscreen.Display(disptype='psychopy', fgc="black", bgc="black", screennr=self.subjVariables['mainMonitor'])
		self.blackScreen = libscreen.Screen(fgc="black", bgc="black")
		self.win = pygaze.expdisplay
		# Stim Paths
		self.imagePath = self.path + '/stimuli/images/'
		self.soundPath = self.path + '/stimuli/sounds/'

		self.activeSoundPath = self.path + '/stimuli/sounds/'
		self.moviePath = self.path + '/stimuli/movies/'
		self.AGPath = self.path + '/stimuli/movies/AGStims/'
		self.imageExt = ['jpg', 'png', 'gif', 'jpeg']

		# Inputs

		if self.subjVariables['eyetracker'] == 'yes':

			attempts = 0
			self.eyetrackers = tr.find_all_eyetrackers()

			while len(self.eyetrackers) == 0 and attempts < 50:
				print("trying to find eyetracker...")
				attempts += 1
				self.eyetrackers = tr.find_all_eyetrackers()

			self.tracker = pygaze.eyetracker.EyeTracker(self.disp)
			print("Eyetracker connected? " + str(self.tracker.connected()))

		# We will always use the keyboard to start the experiment, but it won't always be the main input
		if self.subjVariables['responseDevice'] == 'keyboard':
			print("Using keyboard...")
			self.inputDevice = "keyboard"
			self.validResponses = {'1': 'space', '2': 'left', '3': 'right', '4': 'z', '5': 'enter'}
		# create keyboard object
			self.input = keyboard.Keyboard()

		else:
			self.inputDevice = "mouse"
			print("using mouse...")
			#self.input = libinput.Mouse(mousebuttonlist = [1], timeout = None)


class ExpPresentation(Exp):
	def __init__(self, experiment):
		self.experiment = experiment
		self.lowFreqLabelingBlocks = {}
		self.fillerLabels = ['Hey_check_that_out', 'Hey_look_at_that', 
					   'Do_you_see_it', 'Can_you_see_it']
		
		# Define the actual labels for each low-frequency object
		self.actualLabels = {
			'kita': 'Its_a_kita',
			'manu': 'Its_a_manu'
		}

		self.stimLabels = {
			'object1': 'beevo',
			'object2':'kita',
			'object3':'manu',
			'object4':'guffy'
		}
		self.locations = ['bottomLeft', 'bottomRight', 'topLeft', 'topRight']

		# Familiar objects: one randomly assigned per block (without replacement)
		self.familiarObjects = [
			{'image': 'apple', 'label': 'Label_apple'},
			{'image': 'ball', 'label': 'Label_ball'},
			{'image': 'shoe', 'label': 'Label_shoe'},
			{'image': 'cookie', 'label': 'Label_cookie'},
		]

	def initializeExperiment(self):
		
		# Loading Files Screen
		loadScreen = libscreen.Screen()
		loadScreen.draw_text(text = "Loading Files...", color = "white", fontsize = 48)
		self.experiment.disp.fill(loadScreen)
		self.experiment.disp.show()

		# Load Trials
		familiarizationTrialPath = 'orders/familiarizationTrialOrders/Order' + self.experiment.subjVariables['order'] +".csv"
		activeTrainingTrialPath = 'orders/activeTrainingOrders/ActiveTrainingOrder' + self.experiment.subjVariables['order'] +".csv"
		activeTestTrialPath = 'orders/activeOrders/ActiveOrder' + self.experiment.subjVariables['order'] +".csv"
		lwlTrialPath = 'orders/lwlOrders/LWLOrder' + self.experiment.subjVariables['order'] +".csv"

		(self.familTrialListMatrix, self.trialFieldNames) = importTrials(familiarizationTrialPath, method="sequential")
		(self.activeTrainingTrialsMatrix, self.activeTrainingTrialFieldNames) = importTrials(activeTrainingTrialPath, method="sequential")
		(self.activeTestTrialsMatrix, self.activeTrialFieldNames) = importTrials(activeTestTrialPath, method="sequential")
		(self.lwlTestTrialsMatrix, self.lwlTrialFieldNames) = importTrials(lwlTrialPath, method="sequential")

		self.initializeLowFreqLabeling()
		self.initializeFamiliarObjectTrials()

		self.movieMatrix = loadFilesMovie(self.experiment.moviePath, ['mp4', 'mov'], 'movie', self.experiment.win)
		self.AGmovieMatrix = loadFilesMovie(self.experiment.AGPath, ['mp4'], 'movie', self.experiment.win)
		self.soundMatrix = loadFiles(self.experiment.soundPath, ['.mp3', '.wav', '.aiff'], 'sound')
		self.AGsoundMatrix = loadFiles(self.experiment.AGPath, ['.mp3', '.wav', '.aiff'], 'sound')
		self.imageMatrix = loadFiles(self.experiment.imagePath, ['.png', '.PNG', ".jpg", ".jpeg"], 'image', win = self.experiment.win)
		self.stars = loadFiles(self.experiment.AGPath, ['.jpg'], 'image', self.experiment.win)

		
		self.trigger = 0 # start trigger for eyetracker (0) vs keyboard (1)

		# dimensions MATH ugh

		self.x_length = constants.DISPSIZE[0]
		self.y_length = constants.DISPSIZE[1]
		print(self.x_length, self.y_length)

		self.pos = {'bottomLeft': (-self.x_length/4, -self.y_length/4), 
			  'bottomRight': (self.x_length/4, -self.y_length/4),
					'centerLeft': (-480, 0), 
					'centerRight': (480, 0),
					'topLeft': (-self.x_length/4, self.y_length/4),
					'topRight': (self.x_length/4, self.y_length/4),
					'center': (0, 0),
					'sampleStimLeft': (-600, -150),
					'sampleStimRight': (600, -150),
					'stimleft': (-self.x_length/4, -350),
					'stimright': (self.x_length/4, -350)
					}
		
		aoi_width = 600
		aoi_height = 500
	
		self.posAOIS = {}
		for location, position in self.pos.items():
			pygaze_pos = psychopy_to_pygaze(position, x_offset = aoi_width/2, y_offset = aoi_height/2)
			print(pygaze_pos)
			self.posAOIS[location] = aoi.AOI('rectangle', pos=pygaze_pos, size=(aoi_width, aoi_height))

		# Contingent Timing Settings
		self.firstTriggerThreshold = 150  # (ms) time to accumulate looks before triggering image
		self.awayThreshold = 250  # (ms) time of NA/away looks for contingent ends - should account for blinks. Lower is more sensitive, higher is more forgiving.
		self.noneThreshold = 1  # (ms) time of look to on-screen but non-trigger AOI before contingent ends - should account for shifts

		self.timeoutTime = 15000  # (ms) 30s, length of trial
		self.rect_size = (500, 500)
		self.fam_rect_size = (500, 500)
		self.fam_stim_size = (400, 400)
		self.stim_size = (400,400)
		self.ISI = 500
		self.startSilence = 0
		self.endSilence = 1000

		# sampling threshold - when the gaze will trigger (20 samples = 333.333 ms)
		self.lookAwayPos = (-1,-1)
		self.maxLabelTime = 10000 # (ms) Maximum length of time each image can be sampled before the screen resets.

        # Animation settings for looming
		self.loomDuration = 1  # seconds for full loom cycle
		self.jiggleAmplitude = 5  # degrees
		self.jiggleFrequency = 1  # Hz
		self.wiggleDuration = 2.0 #s
		self.targetSizeFactor = 1.25  # Grow to 150% of original size

		# Build Screens for Image Based Displays (Initial Screen and Active Stuff)

		# INITIAL SCREEN #
		self.initialScreen = libscreen.Screen()
		self.initialImageName = self.experiment.imagePath + "bunnies.gif"
		initialImage = visual.ImageStim(self.experiment.win, self.initialImageName, mask=None, interpolate=True)
		initialImage.setPos(self.pos['center'])

		buildScreenPsychoPy(self.initialScreen, [initialImage])
		print("Screen presented, waiting for keypress...")

	# Active Sampling Test Screen #

	def initializeLowFreqLabeling(self):
		"""
		Initialize random labeling blocks for low-frequency objects.
		For each low-frequency object, randomly select one block (out of 4) to receive the actual label.
		"""
		# Find all unique low-frequency objects by their imageName (label)
		lowFreqObjects = set()
		
		print("DEBUG: Looking for low-frequency objects...")
		for trial in self.familTrialListMatrix.trialList:
			if trial.get('trialType') == 'training':
				condition = trial.get('trialCondition')
				imageName = trial.get('imageName')
				print(f"  Trial: trialCondition='{condition}', imageName='{imageName}'")
				
				if condition == 'lowfreq':
					print(f"    -> FOUND LOW FREQ: {imageName}")
					lowFreqObjects.add(imageName)
		
		print(f"DEBUG: Unique low-frequency objects found: {lowFreqObjects}")
		
		# For each low-frequency object, randomly assign one block to receive the actual label
		for obj in lowFreqObjects:
			self.lowFreqLabelingBlocks[obj] = random.randint(1, 4)
		
		# Log the randomization for analysis purposes
		print("Low-frequency labeling randomization:")
		for obj, block in self.lowFreqLabelingBlocks.items():
			print(f"  {obj}: Block {block} will receive actual label")
		
		# Write randomization to a file for analysis
		randomization_file = f'data/training/lowfreq_randomization_{self.experiment.subjVariables["subjCode"]}.txt'
		with open(randomization_file, 'w') as f:
			f.write("Low-frequency object labeling randomization:\n")
			for obj, block in self.lowFreqLabelingBlocks.items():
				f.write(f"{obj}: Block {block}\n")

	def initializeFamiliarObjectTrials(self):
		"""
		Randomly assign one familiar object to each training block (without replacement),
		and randomly choose its position within the block:
		  0 = before the first HF trial
		  1 = between the two HF trials
		  2 = after the second HF trial
		"""
		objects = list(self.familiarObjects)
		random.shuffle(objects)

		positions = [random.randint(0, 2) for _ in range(4)]

		# Alternate sides across blocks
		sides = ['centerLeft', 'centerRight', 'centerLeft', 'centerRight']
		random.shuffle(sides)

		self.familiarTrialAssignments = {}
		for block_num in range(1, 5):
			self.familiarTrialAssignments[block_num] = {
				'image': objects[block_num - 1]['image'],
				'label': objects[block_num - 1]['label'],
				'position': positions[block_num - 1],
				'location': sides[block_num - 1],
			}

		# Log the randomization
		print("Familiar object trial assignments:")
		for block, info in self.familiarTrialAssignments.items():
			pos_labels = {0: 'before HF trials', 1: 'between HF trials', 2: 'after HF trials'}
			print(f"  Block {block}: {info['image']} at {info['location']}, {pos_labels[info['position']]}")

		# Write to file for analysis
		randomization_file = f'data/training/familiar_randomization_{self.experiment.subjVariables["subjCode"]}.txt'
		with open(randomization_file, 'w') as f:
			f.write("Familiar object trial assignments:\n")
			for block, info in self.familiarTrialAssignments.items():
				pos_labels = {0: 'before HF trials', 1: 'between HF trials', 2: 'after HF trials'}
				f.write(f"Block {block}: {info['image']} at {info['location']}, {pos_labels[info['position']]}\n")

	def getTrialLabel(self, curTrial):
		"""
		Determine what label to use for this trial based on frequency and randomization.
		Returns the label to use and whether it's the actual label or filler.
		"""
		if curTrial.get('trialCondition') != 'lowfreq':
			# For high-frequency and AG trials, always use the original label
			return curTrial['label'], True, 'original'
		
		# For low-frequency trials, check if this block should get the actual label
		imageName = curTrial['imageName']  # This is the object name (kita, manu, etc.)
		currentBlock = int(curTrial['blockID'])  # Convert float to int for comparison
		assignedBlock = self.lowFreqLabelingBlocks.get(imageName)
		
		print(f"DEBUG: Low-freq trial - imageName='{imageName}', currentBlock={currentBlock}, assignedBlock={assignedBlock}")
		
		if currentBlock == assignedBlock:
			# This block gets the actual label - use our defined actual label
			actualLabel = self.actualLabels.get(imageName, curTrial['label'])
			print(f"  -> USING ACTUAL LABEL: '{actualLabel}'")
			return actualLabel, True, 'actual'
		else:
			# This block gets the filler label from the CSV (your hand-curated sequence)
			fillerLabel = curTrial['label']
			print(f"  -> USING CSV FILLER LABEL: '{fillerLabel}'")
			return fillerLabel, False, 'filler'


	def presentScreen(self, screen):
		setAndPresentScreen(self.experiment.disp, screen)
		key = event.waitKeys(keyList=['space', 'enter', 'left', 'right', 'down'])
		print(f"Key pressed: {key}")
		self.experiment.disp.show()

	def _makeFamiliarTrial(self, block_num):
		"""Create a synthetic trial dict for a familiar object trial."""
		info = self.familiarTrialAssignments[block_num]
		return {
			'trialType': 'training',
			'trialCondition': 'familiar',
			'trialID': f'fam_{block_num}',
			'blockID': block_num,
			'targetImage': info['image'],
			'imageLocation': info['location'],
			'imageName': info['image'],
			'label': info['label'],
			'trialDuration': '',
			'trialStartSilence': '',
			'trialEndSilence': '',
			'AG': '', 'AGType': '', 'AGImage': '', 'AGAudio': '',
			'AGVideo': '', 'AGTime': '', 'AGgetInput': '',
			'AGWidth': '', 'AGHeight': '',
		}

	def cycleThroughTrials(self, whichPart):
		curFamilTrialIndex = 1

		if whichPart == "familiarizationPhase":
			# Group trials by block so we can insert familiar trials
			blocks = {}
			other_trials = []  # AG trials not tied to a training block (e.g. final AG)
			for curTrial in self.familTrialListMatrix.trialList:
				block_id = curTrial.get('blockID')
				if block_id and str(block_id).strip():
					block_id = int(float(block_id))
					if block_id not in blocks:
						blocks[block_id] = {'ag': [], 'training': []}
					if curTrial['trialType'] in ('AG', 'PauseAG'):
						blocks[block_id]['ag'].append(curTrial)
					elif curTrial['trialType'] == 'training':
						blocks[block_id]['training'].append(curTrial)
				else:
					other_trials.append(curTrial)

			for block_num in sorted(blocks.keys()):
				block = blocks[block_num]

				# Present AG trials for this block
				for agTrial in block['ag']:
					if agTrial['trialType'] == 'AG':
						self.presentAGTrial(agTrial, self.trialFieldNames, getInput="no", duration=agTrial['AGTime'])
					elif agTrial['trialType'] == 'PauseAG':
						self.presentAGTrial(agTrial, self.trialFieldNames, getInput="yes", duration=0)
					self.experiment.win.flip()
					curFamilTrialIndex += 1

				# Build training trial list with familiar trial inserted
				training_trials = list(block['training'])
				fam_trial = self._makeFamiliarTrial(block_num)
				insert_pos = self.familiarTrialAssignments[block_num]['position']
				training_trials.insert(insert_pos, fam_trial)

				# Present all training trials (HF + familiar)
				for curTrial in training_trials:
					self.presentTrial(curTrial, curFamilTrialIndex, stage="familiarization", getInput="no")
					self.experiment.win.flip()
					curFamilTrialIndex += 1

			# Present any remaining trials (e.g. final AG)
			for curTrial in other_trials:
				if curTrial['trialType'] == 'AG':
					self.presentAGTrial(curTrial, self.trialFieldNames, getInput="no", duration=curTrial['AGTime'])
					self.experiment.win.flip()
				curFamilTrialIndex += 1

		elif whichPart == "activeTraining":
			curActiveTrainingIndex = 1
			for curTrial in self.activeTrainingTrialsMatrix.trialList:
				print(curTrial)
				if curTrial['trialType'] == 'AG':
					self.presentAGTrial(curTrial, self.activeTrainingTrialFieldNames ,getInput = "no", duration = curTrial['AGTime'])
					self.experiment.win.flip()
				if curTrial['trialType'] == 'activeTraining':
					self.presentActiveTrial(curTrial, curActiveTrainingIndex, self.activeTrainingTrialFieldNames, "activeTraining")
					curActiveTrainingIndex += 1

		elif whichPart == "lwlTest":
			curlwlTestIndex = 1
			for curTrial in self.lwlTestTrialsMatrix.trialList:
				print(curTrial)
				if curTrial['trialType'] == 'AG':
					self.presentAGTrial(curTrial, self.lwlTrialFieldNames ,getInput = "no", duration = curTrial['AGTime'])
					self.experiment.win.flip()
				if curTrial['trialType'] == 'test':
					self.presentLWLTrial(curTrial, curlwlTestIndex, self.lwlTrialFieldNames,  
						  curTrial['trialStartSilence'],
						   curTrial['trialAudioDuration'], 
						   curTrial['trialEndSilence'],"LWLTest")
					curlwlTestIndex += 1

		elif whichPart == "activeTest":
			curActiveTestIndex = 1
			for curTrial in self.activeTestTrialsMatrix.trialList:
				print(curTrial)

				self.presentActiveTrial(curTrial, curActiveTestIndex, self.activeTrialFieldNames, "activeTest")
				curActiveTestIndex += 1

	def presentAGTrial(self, curTrial, trialFieldNames, getInput, duration):

		# flip screen
		self.experiment.disp.fill(self.experiment.blackScreen)
		self.experiment.disp.show()

		# pause for duration of ISI
		libtime.pause(self.ISI)
		if self.experiment.subjVariables['eyetracker'] == "yes":
			self.experiment.tracker.start_recording()
			logData = "Experiment %s subjCode %s trialOrder %s" % (
			self.experiment.expName, self.experiment.subjVariables['subjCode'], self.experiment.subjVariables['order'])
			print(trialFieldNames)
			for field in trialFieldNames:
				logData += " "+field+" "+str(curTrial[field])
			#print("would have logged " + logData)
			self.experiment.tracker.log(logData)

		if curTrial['AGType'] == "image":
			# create picture
			curPic = self.imageMatrix[curTrial['AGImage']][0]
			# position in center of screen
			curPic.pos = self.pos['center']
			# create screen
			agScreen = libscreen.Screen()
			# build screen
			buildScreenPsychoPy(agScreen, [curPic])

			# present screen
			# see stimPresPyGaze to see details on setAndPresentScreen
			# basically, it simply fills the display with the specified screen (setting) and then flips (shows) the screen (presenting)
			setAndPresentScreen(self.experiment.disp, agScreen)
			if self.experiment.subjVariables['eyetracker'] == "yes":
				# log event
				self.experiment.tracker.log("presentAGImage")

			if curTrial['AGAudio'] != "none":
				playAndWait(self.soundMatrix[curTrial['AGAudio']], waitFor=0)

				if self.experiment.subjVariables['eyetracker'] == "yes":
					# log event
					self.experiment.tracker.log("presentAGAudio")

			# display for rest of ag Time
			libtime.pause(duration)

		elif curTrial['AGType'] == "movie":

			if curTrial['AGAudio'] != "none":
				curSound = self.AGsoundMatrix[curTrial['AGAudio']]
				#just use the psychopy prefs, not the winsound stuff...
				curSound.play()

			# load movie stim

			mov = self.AGmovieMatrix[curTrial['AGVideo']]
			mov.size = (self.x_length, self.y_length)

			mov.play()

			while not mov.isFinished:
				mov.draw()
				self.experiment.win.flip()
			
			mov.stop()

			#if curTrial['AGAudio'] != "none":
		#		curSound = self.AGsoundMatrix[curTrial['AGAudio']]

		if self.experiment.subjVariables['eyetracker'] == "yes":
			# stop eye tracking
			self.experiment.tracker.log("endAG")
			self.experiment.tracker.stop_recording()

		self.experiment.disp.fill(self.experiment.blackScreen)

	def presentTrial(self, curTrial, curTrialIndex, stage, getInput):
		"""
		Present a familiarization trial with looming PNG images rather than videos.
		
		Parameters:
		-----------
		curTrial : dict
			Current trial information from the CSV
		curTrialIndex : int
			Index of the current trial
		stage : str
			Current experimental stage
		getInput : str
			Whether to get input from participant
		"""
		self.experiment.disp.show()
		libtime.pause(self.ISI)

		labelToUse, isActualLabel, labelType = self.getTrialLabel(curTrial)

		# start eyetracking
		if self.experiment.subjVariables['eyetracker'] == "yes":
			self.experiment.tracker.start_recording()
			logData = "Experiment %s subjCode %s trialOrder %s" % (
				self.experiment.expName, self.experiment.subjVariables['subjCode'],
				self.experiment.subjVariables['order'])

			for field in self.trialFieldNames:
				logData += " "+field+" "+str(curTrial[field])

			logData += f" actualLabel {isActualLabel} labelType {labelType} usedLabel {labelToUse}"
			#print("would have logged " + logData)
			self.experiment.tracker.log(logData)

		

		#grab correct movie, sound, and images
		curSound = self.soundMatrix[labelToUse]

		# set image sizes
		imageName = curTrial['targetImage']
		image = self.imageMatrix[imageName][0]
		print(imageName)
		image.pos = self.pos[curTrial["imageLocation"]]
		image.size = self.fam_stim_size


		rect = visual.Rect(
						self.experiment.win,
						width=self.fam_rect_size[0], height=self.fam_rect_size[1],
						fillColor="lightgray", lineColor=None,
						pos=self.pos[curTrial["imageLocation"]])
		

		# Draw static image for silent preview period (1000ms)
		rect.draw()
		image.draw()
		self.experiment.win.flip()

		trialTimerStart = libtime.get_time()

		if self.experiment.subjVariables['eyetracker'] == "yes":
			self.experiment.tracker.log("startScreen")

		# 1000ms silent preview with static object
		silentPreviewDuration = 1000  # ms
		while (libtime.get_time() - trialTimerStart) < silentPreviewDuration:
			rect.draw()
			image.draw()
			self.experiment.win.flip()

			keys = event.getKeys()
			if 'escape' in keys:
				break

		# Start animation + audio for 4000ms
		imageAnimation = LoomAnimation(
			stim=image,
			win=self.experiment.win,
			init_size=image.size,
			target_size_factor=self.targetSizeFactor,
			loom_in_duration=self.loomDuration,
			loom_out_duration=self.loomDuration,
			wiggle_duration=self.wiggleDuration,
			jiggle_amplitude=self.jiggleAmplitude,
			jiggle_frequency=self.jiggleFrequency,
			looping= False
		)

		curSound.play()

		if self.experiment.subjVariables['eyetracker'] == "yes":
			self.experiment.tracker.log("audioOnset")

		animationDuration = 4000  # ms
		animationStart = libtime.get_time()
		while (libtime.get_time() - animationStart) < animationDuration:
			rect.draw()
			imageAnimation.update()
			self.experiment.win.flip()

			keys = event.getKeys()
			if 'escape' in keys:
				break

		curSound.stop()
		
		libtime.pause(self.endSilence)

		######Stop Eyetracking######

		# trialEndTime
		trialTimerEnd = libtime.get_time()
		# trial time
		trialTime = trialTimerEnd - trialTimerStart
		if self.experiment.subjVariables['eyetracker'] == "yes":
			# stop eye tracking
			self.experiment.tracker.log("endScreen")
			self.experiment.tracker.stop_recording()

		self.experiment.disp.fill()

		fieldVars = []
		for curField in self.trialFieldNames:
			fieldVars.append(curTrial[curField])

		[header, curLine] = createRespNew(self.experiment.subjInfo, self.experiment.subjVariables, self.trialFieldNames,
										  fieldVars,
										  a_curTrialIndex=curTrialIndex,
										  b_trialStart=trialTimerStart,
										  c_expTimer=trialTimerEnd,
										  d_trialTime=trialTime,
										  # Add new fields for labeling info
										  e_actualLabel=isActualLabel,
										  f_labelType=labelType,
										  g_usedLabel=labelToUse,
										  h_originalLabel=curTrial['label'])

		writeToFile(self.experiment.trainingOutputFile, curLine)

	def presentActiveTrial(self, curTrial, curActiveTrialIndex, trialFieldNames, stage,  *args):
		print("Start active")
		csv_header = ["timestamp","eyetrackerLog",  "sampledLook", "avgPOS", "curLook",  "response"]
		trigger_filename = 'data/' + stage + '/' + 'tracking_data_' + self.experiment.subjVariables['subjCode'] + '.txt'
		ctrl = ActiveTrialController(self, curTrial)
		with open(trigger_filename, "w", newline='') as file:
			writer = csv.writer(file)
			writer.writerow(csv_header)

		self.experiment.disp.show()

		bottomLeftStimName = curTrial['bottomLeftStim']
		bottomRightStimName = curTrial['bottomRightStim']
		topLeftStimName = curTrial['topLeftStim']
		topRightStimName = curTrial['topRightStim']
		# Find Psychopy Stim from image matrix
		# Bottom Left
		self.bottomLeftStimImage  = self.imageMatrix[bottomLeftStimName][0]
		self.bottomLeftStimImage.pos = self.pos['bottomLeft']
		self.bottomLeftStimImage.size = self.stim_size

		# Top Left
		self.topLeftStimImage  = self.imageMatrix[topLeftStimName][0]
		self.topLeftStimImage.pos = self.pos['topLeft']
		self.topLeftStimImage.size = self.stim_size

		# Bottom Right
		self.bottomRightStimImage = self.imageMatrix[bottomRightStimName][0]
		self.bottomRightStimImage.pos = self.pos['bottomRight']
		self.bottomRightStimImage.size = self.stim_size

		#Top Right
		self.topRightStimImage = self.imageMatrix[topRightStimName][0]
		self.topRightStimImage.pos = self.pos['topRight']
		self.topRightStimImage.size = self.stim_size

		self.bottomLeftRect = visual.Rect(
			self.experiment.win,
			width=self.fam_rect_size[0], height=self.fam_rect_size[1],
			fillColor="lightgray", lineColor=None,
			pos=self.pos['bottomLeft']
		)

		self.bottomRightRect = visual.Rect(
			self.experiment.win,
			width=self.fam_rect_size[0], height=self.fam_rect_size[1],
			fillColor="lightgray", lineColor=None,
			pos=self.pos['bottomRight']
		)
		self.topLeftRect = visual.Rect(
			self.experiment.win,
			width=self.fam_rect_size[0], height=self.fam_rect_size[1],
			fillColor="lightgray", lineColor=None,
			pos=self.pos['topLeft']
		)

		self.topRightRect = visual.Rect(
			self.experiment.win,
			width=self.fam_rect_size[0], height=self.fam_rect_size[1],
			fillColor="lightgray", lineColor=None,
			pos=self.pos['topRight']
		)

		# Draw background rectangles first, then the images
		#self.leftRect.draw()
		#self.rightRect.draw()
		#self.leftStimImage.draw()
		#self.rightStimImage.draw()
		
		self.experiment.win.flip()

		# Initialize eyetracker

		libtime.pause(self.ISI)

		if self.experiment.subjVariables['eyetracker'] == 'yes':
			self.experiment.tracker.start_recording()
			logData = "Experiment %s subjCode %s trialOrder %s" % (
				self.experiment.expName, self.experiment.subjVariables['subjCode'],
				self.experiment.subjVariables['order'])
			for field in trialFieldNames:
				logData += " " + field + " " + str(curTrial[field])
			self.experiment.tracker.log(logData)

		if self.experiment.subjVariables['eyetracker'] == "yes":
			# log event
			self.experiment.tracker.log("startScreen")

		# Create adnimations
		topLeftAnimation = LoomAnimation(
			stim=self.topLeftStimImage,
			win=self.experiment.win,
			init_size=self.topLeftStimImage.size,
			target_size_factor=self.targetSizeFactor,
			loom_in_duration=self.loomDuration,
			loom_out_duration=self.loomDuration,
			wiggle_duration=self.wiggleDuration,
			jiggle_amplitude=self.jiggleAmplitude,
			jiggle_frequency=self.jiggleFrequency,
			looping= True  # Enable looping for continuous animation
		)
		topRightAnimation = LoomAnimation(
			stim=self.topRightStimImage,
			win=self.experiment.win,
			init_size=self.topRightStimImage.size,
			target_size_factor=self.targetSizeFactor,
			loom_in_duration=self.loomDuration,
			loom_out_duration=self.loomDuration,
			wiggle_duration=self.wiggleDuration,
			jiggle_amplitude=self.jiggleAmplitude,
			jiggle_frequency=self.jiggleFrequency,
			looping= True   # Enable looping for continuous animation
		)

		bottomLeftAnimation = LoomAnimation(
			stim=self.bottomLeftStimImage,
			win=self.experiment.win,
			init_size=self.bottomLeftStimImage.size,
			target_size_factor=self.targetSizeFactor,
			loom_in_duration=self.loomDuration,
			loom_out_duration=self.loomDuration,
			wiggle_duration=self.wiggleDuration,
			jiggle_amplitude=self.jiggleAmplitude,
			jiggle_frequency=self.jiggleFrequency,
			looping= True  # Enable looping for continuous animation
		)
		bottomRightAnimation = LoomAnimation(
			stim=self.bottomRightStimImage,
			win=self.experiment.win,
			init_size=self.bottomRightStimImage.size,
			target_size_factor=self.targetSizeFactor,
			loom_in_duration=self.loomDuration,
			loom_out_duration=self.loomDuration,
			wiggle_duration=self.wiggleDuration,
			jiggle_amplitude=self.jiggleAmplitude,
			jiggle_frequency=self.jiggleFrequency,
			looping= True   # Enable looping for continuous animation
		)

		# pause for non-contingent frozen display
		
		# start playing each video for 1 sec
		
		self.activefamtimeoutTime = 1500

		activefamstarttopleft = libtime.get_time()
		while libtime.get_time() - activefamstarttopleft < self.activefamtimeoutTime:
			self.topLeftRect.draw()
			self.topLeftStimImage.draw()
			self.experiment.win.flip()

		activefamstarttopright = libtime.get_time()
		while libtime.get_time() - activefamstarttopright < self.activefamtimeoutTime:
			self.topRightRect.draw()
			self.topRightStimImage.draw() 
			self.experiment.win.flip()

		activefamstartbottomright = libtime.get_time()
		while libtime.get_time() - activefamstartbottomright < self.activefamtimeoutTime:
			self.bottomRightRect.draw()
			self.bottomRightStimImage.draw()
			self.experiment.win.flip()
		
		activefamstartbottomleft = libtime.get_time()
		while libtime.get_time() - activefamstartbottomleft < self.activefamtimeoutTime:
			self.bottomLeftRect.draw()
			self.bottomLeftStimImage.draw()
			self.experiment.win.flip()

		libtime.pause(500)

		start = libtime.get_time()
		while libtime.get_time() - start < 1500:
			stim = visual.TextStim(self.experiment.win, '+',
                       color="white")
			stim.size = 300
			#self.rightStimMov.draw()
			#self.leftStimMov.draw()
			stim.draw()
			self.experiment.win.flip()

		if self.experiment.subjVariables['eyetracker'] == "yes":
			# log event
			self.experiment.tracker.log("startContingent")
		log_file_list = [libtime.get_time(), "startContingent", None
							 , None, None
							 , None]
		with open(trigger_filename, 'a', newline='') as file:
			writer = csv.writer(file)
			writer.writerow(log_file_list)
		
		ctrl.run(timeout_s=self.timeoutTime / 1000.0)
		
		self.experiment.disp.fill(self.experiment.blackScreen)
		self.experiment.disp.show()
		# Clear screen
		self.experiment.disp.fill(self.experiment.blackScreen)
		self.experiment.disp.show()

		# Record trial end
		trialTimerEnd = libtime.get_time()
		#trialTime = trialTimerEnd - trialTimerStart
		
		if self.experiment.subjVariables['eyetracker'] == "yes":
			# Stop eye tracking
			self.experiment.tracker.log("stopScreen")
			self.experiment.tracker.stop_recording()

	def presentLWLTrial(self, curTrial, culwlTestIndex, trialFieldNames, 
					 trialStartSilence, trialAudioDuration, trialEndSilence, stage):
		print("start LWL")
		self.experiment.disp.show()
		libtime.pause(self.ISI + random.choice([0, 100, 200]))

		print(curTrial)
		if self.experiment.subjVariables['eyetracker'] == "yes":
			self.experiment.tracker.start_recording()
			logData = "Experiment %s subjCode %s trialOrder %s" % (
				self.experiment.expName, self.experiment.subjVariables['subjCode'],
				self.experiment.subjVariables['order'])

			for field in trialFieldNames:
				logData += " "+field+" "+str(curTrial[field])
			print("would have logged " + logData)
			self.experiment.tracker.log(logData)
		
		curTargetLocation = curTrial['TargetObjectPos']
		curTargetTrialCoordinates = self.pos[curTargetLocation]

		curDistracterLocation = curTrial['DistracterObjectPos']
		curDistracterTrialCoordinates = self.pos[curDistracterLocation]

		curTargetPic = self.imageMatrix[curTrial['TargetImage']][0]  # psychopy image stimulus
		curDistracterPic = self.imageMatrix[curTrial['DistracterImage']][0]  # psychopy image stimulus
		curTargetPic.size = self.stim_size
		curTargetPic.pos = curTargetTrialCoordinates
		curDistracterPic.size = self.stim_size
		curDistracterPic.pos = curDistracterTrialCoordinates
		targetRect = visual.Rect(
			self.experiment.win,
			width=600, height=600,
			fillColor="lightgray", lineColor=None,
			pos=curTargetTrialCoordinates
		)

		distracterRect = visual.Rect(
			self.experiment.win,
			width=600, height=600,
			fillColor="lightgray", lineColor=None,
			pos=curDistracterTrialCoordinates
		)
		testScreen = libscreen.Screen()
		buildScreenPsychoPy(testScreen, [targetRect, distracterRect])
		buildScreenPsychoPy(testScreen, [curTargetPic, curDistracterPic])

		trialTimerStart = libtime.get_time()
		setAndPresentScreen(self.experiment.disp, testScreen)

		if self.experiment.subjVariables['eyetracker'] == "yes":
            # log event
			self.experiment.tracker.log("testScreen")
		
		libtime.pause(trialStartSilence)

		playAndWait(self.soundMatrix[curTrial['Audio']], waitFor=0)

		if self.experiment.subjVariables['eyetracker'] == "yes":
            # log event
			self.experiment.tracker.log("audioOnset")

		libtime.pause(trialAudioDuration)

		if self.experiment.subjVariables['eyetracker'] == "yes":
			self.experiment.tracker.log("audioOffset")
        # silence at end of trial

		libtime.pause(trialEndSilence)

		self.experiment.disp.fill()
	

	def EndDisp(self):
		# show the screen with no stars filled in
		# self.stars['0'][0].draw()
		# print(self.stars)
		# win.flip()

		curStar = self.stars['0'][0]
		curStar.size = (self.x_length, self.y_length)
		# create screen
		endScreen = libscreen.Screen()
		# build screen
		buildScreenPsychoPy(endScreen, [curStar])

		# present screen
		setAndPresentScreen(self.experiment.disp, endScreen)

		core.wait(1)

		# iterate to fill in each star
		for i in range(1, 6, 1):
			# self.stars[str(i)][0].draw()
			#  win.flip()
			curStar = self.stars[str(i)][0]
			curStar.size = (self.x_length, self.y_length)
			# build screen
			buildScreenPsychoPy(endScreen, [curStar])
			# present screen
			setAndPresentScreen(self.experiment.disp, endScreen)

			self.AGsoundMatrix['ding'].play()
			core.wait(.5)
			self.AGsoundMatrix['ding'].stop()

		# have the stars jiggle
		self.AGsoundMatrix['applause'].play()
		self.AGsoundMatrix['done'].volume = 2
		self.AGsoundMatrix['done'].play()

		for i in range(4):
			# self.stars['5'][0].draw()
			# win.flip()
			curStar = self.stars['5'][0]
			curStar.size = (self.x_length, self.y_length)
			# build screen
			buildScreenPsychoPy(endScreen, [curStar])
			# present screen
			setAndPresentScreen(self.experiment.disp, endScreen)

			core.wait(.5)
			# self.stars['5_left'][0].draw()
			# win.flip()

			curStar = self.stars['5_left'][0]
			curStar.size = (self.x_length, self.y_length)
			# build screen
			buildScreenPsychoPy(endScreen, [curStar])
			# present screen
			setAndPresentScreen(self.experiment.disp, endScreen)
			core.wait(.5)

			# self.stars['5'][0].draw()
			# win.flip()
			# core.wait(.5)
			# self.stars['5_right'][0].draw()
			# win.flip()
			# core.wait(.5)

			curStar = self.stars['5'][0]
			curStar.size = (self.x_length, self.y_length)
			# build screen
			buildScreenPsychoPy(endScreen, [curStar])
			# present screen
			setAndPresentScreen(self.experiment.disp, endScreen)

			core.wait(.5)
			# self.stars['5_left'][0].draw()
			# win.flip()

			curStar = self.stars['5_right'][0]
			curStar.size = (self.x_length, self.y_length)
			# build screen
			buildScreenPsychoPy(endScreen, [curStar])
			# present screen
			setAndPresentScreen(self.experiment.disp, endScreen)
			core.wait(.5)


currentExp = Exp()

currentPresentation = ExpPresentation(currentExp)

currentPresentation.initializeExperiment()
currentPresentation.presentScreen(currentPresentation.initialScreen)
currentPresentation.cycleThroughTrials(whichPart = "familiarizationPhase")
#currentPresentation.cycleThroughTrials(whichPart= "lwlTest")
currentPresentation.cycleThroughTrials(whichPart = "activeTraining")
currentPresentation.cycleThroughTrials(whichPart = "activeTest")
currentPresentation.EndDisp()