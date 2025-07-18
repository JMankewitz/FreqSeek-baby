"""These are pygaze specific functions and rely on pygaze modules and presentation systems"""
from pygaze import libscreen
from pygaze import libtime


def buildScreenPsychoPy(screen, stimuli):
	"""Adds psychopy stimuli to a screen"""
	"""Stimuli can be a list or a single draw-able stimulus"""
	if type(stimuli).__name__ == "list":
		for curStim in stimuli:
			screen.screen.append(curStim)
	else:
		screen.screen.append
	return


def setAndPresentScreen(display, screen, duration=0):
	"""Sets display with a given screen and displays that screen"""
	"""duration can be set to a specific time to display screen for"""
	"""otherwise, the function returns immediately (duration=0)"""
	display.fill(screen)
	if duration == 0:  # single frame
		display.show()
	else:
		display.show()
		# relies on pygaze's libtime module
		libtime.pause(duration)

def psychopy_to_pygaze(psychopy_coord, screen_width=1920, screen_height=1080, y_offset=0, x_offset = 0):
    """
    Converts a position from PsychoPy (origin at center) to pygaze (origin at top left)
    
    Parameters:
      psychopy_coord: Tuple (x, y) in PsychoPy coordinates.
      screen_width: Width of the screen (default 1920).
      screen_height: Height of the screen (default 1080).
    
    Returns:
      Tuple (x', y') representing the center coordinate for pygaze.
    """
    x, y = psychopy_coord
    # Convert from center origin to top-left origin
    pyg_x = x + (screen_width / 2) - x_offset
    pyg_y = (screen_height / 2) - y - y_offset  # Flip y-axis (in psychopy, +y is up; in pygaze, +y is down)
    return (pyg_x, pyg_y)
