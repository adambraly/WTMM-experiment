#########################################################################
# 					Last updated 7/18/2014          #
# 					Author: Adam Braly              #
# 					email: abraly@gmail.com		#
#									#		
# The contents of this file are for use by Thomas Taylor 		#
# at the University of Central Oklahoma with the express purpose	#
# of data collection for a Master's thesis       			#
#									#
# The astute programmer will note that this code is laden with 		#
# departures from convention. This is an initial attempt to use the	#
# python programming language, and this classless, one-off project was  #
# designed and revised without any consideration for re-usability. 	#
# I can safely assume that these variables shall remain unaltered at	# 
# run-time in a strict laboratory environment. The calamitous number 	#
# of global variables is enough to burden the light-hearted and 	#
# will surely anger the programming gods.				#
# 									#
#									#
#                       						#
#    									#
# In an attempt to replicate the findings of this project, you may	#
# reuse this code with permission. It will not be published under the	#
# GNU license. If you reuse this code, or any part thereof, for 	#
# commercial or monetary gain, you are					#
# unabashedly awful.							#
#									#
#########################################################################
import pygame
from pygame.locals import *
import random
import time
import sys
import xlwt
import ConfigParser

# pygame setup
pygame.init() # initialize pygame
pygame.mixer.init(44100, -16, 2, 2048) # initialize sound mixer
pygame.mouse.set_visible(1) # make mouse cursor visible

# attempt to load sound file
try:
	tone = pygame.mixer.Sound("stim\sound2.wav")
	print 'sound loaded successfully!'
except pygame.error, message:
    print 'Cannot load sound file'
    raise SystemExit, message



## vars ##

dirty_rects		= [] # rectangle list to update squares that have been drawn on only; faster than calling display.update()
new_stim		= []
new_stim_pos	= []

# empty lists for data reporting
stimulus		= []
location		= []
soa				= []
correct			= []
mouse_location	= []

left_stim		= [0, 974] #img is 50x50 pixels; 0,974 + 0,50 = (0,1024): maximum bottom left corner
right_stim		= [1230, 974] 
cursor_left		= [0, 512]
cursor_right	= [1280, 512]
stepping		= [0, 0, 0, 0, 0]
stepping_indices= [0, 0, 0, 0, 0, 0] # stepping_indices[0] = Slice 1 etc.. [i]+1
step_values		= [0, 0, 0, 0, 0, 0] # step_values[0] = Slice 1 value..  
slice_num_corr 	= [0, 0, 0, 0, 0, 0]
curr_slice		= 0
direction		= -1 # -1: none, 0: down, 1: up
corrAns			= 0 # 0=none, 1=T, 2=L
num_corr		= 0
ini_step		= 0
multi			= 0

part_ID			= 0
participant		= 0
trials			= 0
trials_ID		= 0
percent_corr	= -1

# excel sheet setup
wbk		= xlwt.Workbook(encoding="utf-8")
sheet	= wbk.add_sheet('Python')

# six, 5px ranges
slice_one   = [180,181,182,183,184,185]
slice_two   = [360,361,362,363,364,365]
slice_three = [545,546,547,548,549,550]
slice_four  = [730,731,732,733,734,735]
slice_five  = [910,911,912,913,914,915]
slice_six   = [1096,1097,1098,1099,1100]

# setup the window
pygame.display.set_caption('Experiment 1.4') # window title

black			= [0,0,0] # background color
screen_size		= [1280, 1024] # resolution
center_screen	= [(screen_size[0] / 2), (screen_size[1] / 2)] # center of the screen; 0,0 is top left
flags			= pygame.FULLSCREEN
screen			= pygame.display.set_mode(screen_size, flags) # set window size @param1, size @param 2, flags

# in my global mess, I couldn't think of way to initialize this variable without loading an actual image
# that being said, instruction screens will default to English - on Chinese, postInst is re-assigned.
#preInst			= pygame.image.load(r"stim\0.jpg").convert()
#postInst		= pygame.image.load(r"stim\0.jpg").convert()


## function definitions ##

# function to fill stepping from config.ini
def load_config():
	global step_values
	global stepping
	global participant
	global trials
	global ini_step
	global soa_1
	global soa_2
	global soa_3
	global soa_4
	global soa_5
	global img_T
	global img_L
	global preInst
	global postInst
	global fixation
	lang = ""
	prev = 0
	
	config = ConfigParser.ConfigParser()
	config.read("config.ini")
	
	participant = config.getint("Thesis", "ID")
	trials = config.getint("Thesis", "TRIALS")
	ini_step = config.getfloat("Thesis", "FIRST_STEP")
	lang = config.get("Thesis", "LANG")
	# load images
	if lang.lower() == "e":
		preInst		= pygame.image.load("stim\Instructions.jpg").convert()
		postInst	= pygame.image.load("stim\Instructions2.jpg").convert()
		img_T		= pygame.image.load("stim\stimT.jpg").convert() # load image and convert; the new Surface will have the same pixel format as the display Surface. This is always the fastest format for blitting 
		img_L 		= pygame.image.load("stim\stimL.jpg").convert()
		fixation	= pygame.image.load("stim\cross.jpg").convert()
	elif lang.lower() == "c":
		preInst		= pygame.image.load("stim\CHInstructions1.jpg").convert()
		postInst	= pygame.image.load("stim\CHInstructions2.jpg").convert()
		img_T		= pygame.image.load("stim\CHstimT.jpg").convert() # load image and convert; the new Surface will have the same pixel format as the display Surface. This is always the fastest format for blitting 
		img_L 		= pygame.image.load("stim\CHstimL.jpg").convert()
		fixation	= pygame.image.load("stim\cross.jpg").convert()
	else:
		print "Language option not set in config file, no stimuli loaded"
	
	for i in range(0,6):
		step_values[i] = ini_step
		
	for i in range(0,5):
		stepping[i] = config.getfloat("Thesis", "SOA_" + repr(i+1))
	
	for i in range(0,6):
		print step_values[i]
	for i in range(0,5):
		print stepping[i]
		
# fills the screen with black and flips
def flip():
	screen.fill(black)
	return pygame.display.flip()

# function to clear only the rectangles that have been drawn @param: list of [x,y] positions
def clear_rects(x): 
	screen.fill(black) # fill with black background
	pygame.display.update(x) # update only our dirty rects with black
	for i in range(len(x)): # iterate through list of rects, we only want to clear recently created rects so we clear the list afterward
		for each in x: # at each index, remove
			x.remove(each) # call remove

# function to display instruction screen @param: stimulus image			
def display_instructions(stim):
	screen.blit(stim, (0,100))
	pygame.display.flip()
	return 0
	
# function to display fixation point @param: stimulus image
def display_fixation(stim):
	screen.blit(stim, (0, 0))
	pygame.display.flip()
	return 0

# function to randomize stimuli
# modifies the global value of new_stim & corrAns
# appends character to stimulus list
def randomize_stim():
	rand_stim = random.randrange(1,3)
	rand_stim_pos = random.randrange(8,10)
	global new_stim
	global corrAns
	global new_stim_pos
	global location
	if rand_stim == 1:
		new_stim = img_T
		corrAns = 1
		stimulus.append("T")
	else:
		new_stim = img_L
		corrAns = 2
		stimulus.append("L")
		
	if rand_stim_pos == 8:
		new_stim_pos = left_stim
		location.append("Left")
	else:
		new_stim_pos = right_stim
		location.append("Right")

# function to display stimulus and flip @param: x value passed
# appends position to dirty list
def display_stim(x_pos):
	global curr_slice
		
	appear = screen.blit(new_stim,(new_stim_pos)) # display @params: img def and coordinates
	pygame.display.flip()
	print 'Position at stim appearance %s, in slice %s' % (x_pos, curr_slice) # debugging pos at stim displayed
	print 'corr ans is %s in display_stim()' % corrAns
	dirty_rects.append(appear) # add pos to dirty list
	
	
# function to assign random slice 
def rand_interval():

	global curr_slice
	
	rand_val = random.randrange(1,7)
	if rand_val == 1:
		mouse_location.append("Slice 1")
		curr_slice = 1
		return slice_one
	if rand_val == 2:
		mouse_location.append("Slice 2")
		curr_slice = 2
		return slice_two
	if rand_val == 3:
		mouse_location.append("Slice 3")
		curr_slice = 3
		return slice_three
	if rand_val == 4:
		mouse_location.append("Slice 4")
		curr_slice = 4
		return slice_four
	if rand_val == 5:
		mouse_location.append("Slice 5")
		curr_slice = 5
		return slice_five
	if rand_val == 6:
		mouse_location.append("Slice 6")
		curr_slice = 6
		return slice_six

# function to check if mouse x pos is in the slice @param1: passed random slice
# @param2: passed x position @param3: passed boolean displayed		
def check_slice(slice, x, displayed):
	if displayed == False:
		for item in slice:
			if item == x:
				return True
	else:
		return False
	#for item in slice:
	#	if item == x and displayed == False:
	#		return True
	#		break
	
# function to check if key press is correct
# perhaps redundant after implementing global variable correct			
def correct_ans(keypress, corrAns):
	if keypress == 1 and corrAns == 1:
		return True
	if keypress == 2 and corrAns == 2:
		return True
	else:
		return False

# function attempt at single staircase structure @param1: up or down @param2: curr_slice
# no switch statement in python? MADNESS!
def staircase(direction, c_slice):
	
	adj_slice_name = -1 # variable for explicitly naming slices [i] + 1
	global stepping_indices
	global step_values
	global stepping
	global slice_num_corr
	
	
	if c_slice > 0: # unnecessary comment line
		if direction == 0: # stepping up
			for i in (range(0,6)): # 0,1,2,3,4,5  each index of stepping_indices
				adj_slice_name = i + 1 # our naming adjustment
				if adj_slice_name == c_slice: # are we at the correct slice?
					for j in (range(0,5)): # 0,1,2,3,4 each index of step_values
						print j # debug value of j
						print stepping_indices[i] # debug value of stepping_indices before we modify
						if j == stepping_indices[i]: # are we at the value for current stepping_indices?
							print 'Slice %s stepping up from index %s' % (adj_slice_name, j) # debug stepping
							step_values[i] *= stepping[j] # step up
							if stepping_indices[i] < 4: # stepping has 5 indices 0,1,2,3,4 - don't go over 4!
								stepping_indices[i] += 1 # increase the value
							slice_num_corr[i] = 0 # reset the number correct
							print stepping_indices[i] # debug value after
							print step_values[i] #debug value after
							break # we did things, so let's bail!
						
		if direction == 1: # stepping down
			for i in (range(0,6)): # 0,1,2,3,4,5 each index of stepping_indices
				adj_slice_name = i + 1 # our naming adjustment
				if adj_slice_name == c_slice: # are we at the correct slice?
					for j in (range(0,5)): # 0,1,2,3,4 each index of step_values
						print j #debug value of j
						print stepping_indices[i] # debug value of stepping_indices before we modify
						if j == stepping_indices[i]: # are we at the value for current stepping_indices?
							print 'Slice %s stepping down from index %s' % (adj_slice_name, j) # debug stepping
							step_values[i] /= stepping[j] # step down
							if stepping_indices[i] > 1: # we need to stay above one, otherwise we go negative!
								stepping_indices[i] -= 1 # decrease the value
							slice_num_corr[i] = 0 # reset the number correct
							print stepping_indices[i] # debug value after
							print step_values[i] # debug value after
							break # get to tha chopppaaa!
	else:
		print 'Slice number was 0, error...' # are you still reading these?
					
# function to determine if cursor is on boundary @param: current x value
def on_boundary(x):
	return not x < 1279

# function to debug stepping values and stimulus presentation @param1: stepping pos
# @param2: list of dirt rects
# calls clear_rects 
def clear_stim(step_pos, dirty):
	s = "sleeping for: " 
	e = " seconds.."
	print (s + repr(step_pos) + e) # playing with concatenation	
	time.sleep(step_pos) # sleep for current step value
	clear_rects(dirty) # clear all positions drawn on # did i just inception a function?

	
# function to write data to excel file	
def write_data():
	global location
	global stimulus
	global soa
	global correct
	global mouse_location
	global wbk
	global num_corr
	global participant
	global percent_corr
	
	sheet.write(0, 0, "ID")
	sheet.write(0, 1, "Pres. Order")
	sheet.write(0, 2, "Mouse Location")
	sheet.write(0, 3, "Location")
	sheet.write(0, 4, "Stimulus")
	sheet.write(0, 5, "Condition")
	sheet.write(0, 6, "SOA")
	sheet.write(0, 7, "Correct Answer")
	sheet.write(0, 8, "Percentage Correct")
	
	## loops to write data from our lists ##
	i = 0
	for item in location:
		i += 1
		sheet.write(i, 0, participant)
		sheet.write(i, 3, item)
		
	
	j = 0
	for item in stimulus:
		j += 1
		sheet.write(j, 4, item)
			
	k = 0
	for item in soa:
		k += 1
		sheet.write(k, 6, item)
		
	m = 0
	for item in correct:
		m += 1
		sheet.write(m, 7, item)
		
	n = 0
	for item in mouse_location:
		n += 1
		sheet.write(n, 2, item)
	
	if percent_corr < 0:
		sheet.write(1, 8, "N/A")
	else:
		sheet.write(1, 8, percent_corr)
		
	wbk.save(r"data\%s.xls" % participant)

## main function ##	
def main():
	global participant
	global trials
	global corrAns
	global num_corr
	global ini_step
	global multi
	
	global displayed # 1 = t, 2 = l
	global percent_corr
	global curr_slice
	global direction
	global stepping_indices
	global stepping
	global step_values
	global slice_num_corr
	
	load_config()
	#flip()
	
	inst_finished = False # boolean value for instruction loop
	display_instructions(preInst)  # show them the goods
	start = time.clock() # experiment timer, have I even used this?
	
	corrAns		= 0
	num_corr	= 0
	displayed	= 0
	curr_slice 	= 0
	direction	= -1
	
	
	
	
	while inst_finished == False: # poll for events while instructions are displayed
		event = pygame.event.poll() 
		if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE): # user quits
			write_data() # write what we have on exit
			pygame.quit() # quite pygame
			sys.exit() # quit running because user said so
		if (event.type == KEYDOWN and event.key == K_SPACE): # user hits spacebar
			inst_finished = True # instructions done, exit our while loop
			flip() # call our flip method
		
		if inst_finished == True: # did we successfully display instructions?
			for i in range(0,trials): # iterations by trial
				display_fixation(fixation) # display fixation target
				contRoutine = True # boolean flag to break after stimulus is cleared
				contResponse = True # boolean flag to break after user response
				on_screen = False # has the stimulus been on screen?
				time.sleep(2) # for good measure?
				pygame.mouse.set_pos(cursor_left) # set cursor position to left center
				tone.play(loops=0, maxtime=500)# play sound
				random_slice = rand_interval() # compute random interval and assign to random_slice
				randomize_stim() # randomize T or L and Left or Right 
				displayed = 0 # what did we display? # 1 = t, 2 = l
				while contRoutine: # good to go
					event = pygame.event.poll() # poll for events
					if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE): # user quits
						write_data() # write what we have on exit
						pygame.quit() # quit pygame
						sys.exit() # quit running because user said so
					if event.type == MOUSEMOTION: # mouse is moving
						x,y = pygame.mouse.get_pos() # get mouse position
						#print x,y #debug mouse position
						if (not on_boundary(x)): # are we on the boundary?	
							if check_slice(random_slice, x, on_screen): # did we catch a mouse position?
								display_stim(x) # display stim - passing x for debug
								on_screen = True # yes
								for i in (range(0,6)): # 0,1,2,3,4,5 stepping_indices[i]
									adj = i + 1 # call it like it is
									if adj == curr_slice: # are we there yet?
										soa.append(step_values[i]) # append value at index
										if corrAns == 1: # t is the correct answer
											displayed = 1 # t was displayed
											clear_stim(step_values[i], dirty_rects) # cleanup
											break # We're out!
										
										elif corrAns == 2: # l is the correct answer
											displayed = 2 # l was displayed
											clear_stim(step_values[i], dirty_rects) # cleanup
											break # We're really out!
									
								
						elif ((on_boundary(x)) and (not on_screen)): #at edge & not displayed
							display_instructions(postInst) # display keypress instructions
							print "Error: No stimulus presented" # words and stuff
							soa.append('999') # append no value
							contRoutine = False # break to keypress handler
							
						else: # implies on_boundary and on_screen
							display_instructions(postInst) # display keypress instructions
							contRoutine = False # break to keypress handler
							
				
				while contResponse: # ready to listen for input
					event2 = pygame.event.poll() # possible re-use of prior event?
					if event2.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE): # user quits
						write_data() # quickly! save that data!
						pygame.quit() # quit pygame
						sys.exit() # quit running because user said so
					if (event2.type == KEYDOWN and event2.key == K_t): # user pushed T
						if (on_screen): # was it even there?
							if correct_ans(1, corrAns):  # redundant function? can't I just use if corrAns == 1?
								for i in (range(0,6)): # 0,1,2,3,4,5 stepping_indices[i]
									adj = i + 1 # call it like it is
									if adj == curr_slice: # are we there yet?
										slice_num_corr[i] += 1 #################working?
										num_corr += 1 
										print 'T is Correct!' 
										correct.append("Y")
										if slice_num_corr[i] == 2: #################working?
											staircase(0, curr_slice) #################working?
							else:
								print 'T is Incorrect!'
								correct.append("N")
								staircase(1, curr_slice) #################working?
								
						else: # wasn't there
							print 'User pushed T, there was no correct answer' 
							correct.append("999")
						contResponse = False # break to next trial

					if (event2.type == KEYDOWN and event2.key == K_l): # user pushed L
						if (on_screen): # was it there?
							if correct_ans(2, corrAns): # redundant function? can't I just use if corrAns == 2?
								for i in (range(0,6)): # 0,1,2,3,4,5 stepping_indices[i]
									adj = i + 1 # call it like it is
									if adj == curr_slice: # are we there yet?
										slice_num_corr[i] += 1 #################working?
										num_corr += 1
										print 'L is Correct!'
										correct.append("Y")
										if slice_num_corr[i] == 2: #################working?
											staircase(0, curr_slice) #################working?
							else:
								print 'L is Incorrect!'
								correct.append("N")
								staircase(1, curr_slice) #################working?
								
						else: # wasn't there
							print 'User pushed L, there was no correct answer'
							correct.append("999")
						contResponse = False # break to next trial

	percent_corr = (num_corr / float(trials)) * 100 # calculate percentage correct. Excludes 999 fields
	write_data() # write the data for real, though
	time.sleep(1) # seems good?
	pygame.display.quit() # kill the display
	pygame.quit() # kill pygame
	sys.exit() # kill the process
	
if __name__ == '__main__': # only run as a main program - not module
    main()
