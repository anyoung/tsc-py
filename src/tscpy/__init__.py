#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  __init__.py
#  Jul 29, 2015 17:26:13 EDT
#  Copyright 2015
#         
#  Andre Young <andre.young@cfa.harvard.edu>
#  Harvard-Smithsonian Center for Astrophysics
#  60 Garden Street, Cambridge
#  MA 02138
#  
#  Changelog:
#  	AY: Created 2015-07-29

"""
Python interface to Timing Solutions Phase Noise Test Set via telnet
"""

import instruments
import plotter

#~ if __name__ == '__main__':
	#~ # imports for example run
	#~ from contextlib import closing
	#~ from matplotlib.pytplot import ion
	#~ # turn on interactive plotting
	#~ ion()
	#~ # define address for tsc box
	#~ HOST = '128.171.116.229'
	#~ PORT = '1299'
	# open connection to adev box so that it closes properly
	#~ with closing(TSC5120A(HOST,PORT)) as tsc5120a:
		#~ if tsc5120a.connected:
			#~ fcount = tsc5120a.get_fcounter()
			#~ adev = tsc5120a.get_adev()
			#~ tsc5120a.plot_adev(adev)
#~ 
