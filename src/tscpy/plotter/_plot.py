#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  _plot.py
#  Jul 29, 2015 17:54:16 EDT
#  Copyright 2015
#         
#  Andre Young <andre.young@cfa.harvard.edu>
#  Harvard-Smithsonian Center for Astrophysics
#  60 Garden Street, Cambridge
#  MA 02138
#  
#  Changelog:
#  	AY: Created 2015-07-29

def _plot_init():
	from datetime import datetime
	from matplotlib.pyplot import figure
	fig = figure()
	fig.add_axes()
	ax = fig.gca()
	return fig,ax

def plot_adev(adevs,tag='',tsc=None):
	fig,ax = _plot_init()
	for adev in adevs:
		ax.errorbar(adev['adev']['tau'],adev['adev']['adev'],xerr=None,yerr=adev['adev']['err'],label="tau0 = {0}, neq bw = {1}".format(adev['TAU0'],adev['NEQBW']))
	ax.loglog()
	ax.grid(b=True,which='major',linestyle='--')
	ax.grid(b=True,which='mminor',linestyle=':')
	ax.legend()
	ax.set_xlabel('tau [s]')
	ax.set_ylabel('Allan deviation')
	at_str = '' if tsc == None else '@ '+str(tsc.socket[0])
	ax.set_title('{0}TSC5120A {1}: Allan deviation data captured at {2}.'.format(tag,at_str,str(datetime.now())))
	return fig

