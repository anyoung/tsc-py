#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  _tsc5120a.py
#  Jul 29, 2015 17:26:37 EDT
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
tscpy class for the TSC5120A instrument.
"""

from numpy import loadtxt, array
from re import finditer, search
from StringIO import StringIO
from telnetlib import Telnet, socket
from time import sleep

WAIT_AFTER_CONNECT = 1.0
WAIT_AFTER_SEND = 0.1
REGEX_FPNUM = '[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?'

class TSC5120A:
	
	commands = {'SHOW':'show'}
	
	show_params = {'ADEV':'adev','SPECTRUM':'spectrum','SPURS':'spurs',
					'FCOUNTER':'fcounter','FREQ':'freq','PHASEDIFF':'phasediff',
					'INPUTS':'inputs','IPN':'ipn','TIMECONSTANT':'timeconstant',
					'TAU0':'tau0'}
	
	_tc = None
	
	@property
	def connected(self):
		return self._connected
	
	@property 
	def last_read(self):
		return self._last_read
		
	@property
	def socket(self):
		return self._socket
	
	@property
	def tc(self):
		return self._tc
	
	def __init__(self,host,port):
		self._tc = Telnet(host,port)
		self._socket = (host,port)
		sleep(WAIT_AFTER_CONNECT)
		self._receive()
		# for some reason first send-receive does not work, so dummy
		tmp = self._last_read
		if tmp.find('Welcome') == -1:
			self.tc.close()
			self._connected = False
			self._last_read = None
			self._socket = None
			self._tc = None
		else:
			self._show(TSC5120A.show_params.keys()[0])
			self._connected = True
			self._last_read = tmp
	
	def close(self):
		self.tc.close()
		self._last_read = None
	
	# raw communication
	def _receive(self):
		try:
			raw_recv = self.tc.read_very_eager()
			suffix_remove_str = '\r='+self.socket[0]+' > '
			idx_suffix = raw_recv.find(suffix_remove_str)
			if not idx_suffix == -1:
				raw_recv = raw_recv[:idx_suffix]
			self._last_read = raw_recv
			return self._last_read
		except EOFError:
			return None
	
	def _send(self,snd):
		try:
			self.tc.write(snd)
			sleep(WAIT_AFTER_SEND)
			return True
		except socket.error:
			return False
	
	def _show(self,what):
		snd = self.commands['SHOW'] + ' ' + self.show_params[what] + '\n'
		if not self._send(snd):
			return None
		return self._receive()
	
	# parse return values
	def _parse_adev(self,adev_str):
		# block header regex
		regex_header_tau = 'TAU0'
		regex_header_neqbw_tag = 'NEQ[\s]+BW'
		regex_header_neqbw_full = '[\s]+\('+regex_header_neqbw_tag+'\:[\s]+'+REGEX_FPNUM+'[\s]+[a-zA-Z]+\)'
		regex_header = regex_header_tau+'\:[\s]+'+REGEX_FPNUM+regex_header_neqbw_full
		# block line regex
		regex_line_tau = 'tau'
		regex_line_adev = 'adev'
		regex_line_err = 'err'
		regex_line = '[\s]*'+regex_line_tau+'\:[\s]+'+REGEX_FPNUM+'[\s]+'+regex_line_adev+'\:[\s]+'+REGEX_FPNUM+'[\s]+'+regex_line_err+'\:[\s]+'+'\+\/\-'+REGEX_FPNUM
		adev_blocks = []
		# parse adev return text as numpy array
		remo_iter_blocks = finditer(regex_header,adev_str)
		for ri in remo_iter_blocks:
			# parse header
			header_str = adev_str[ri.start():ri.end()]
			remo = search(regex_header_tau+'\:[\s]+'+REGEX_FPNUM,header_str)
			tmp_str = header_str[remo.start():remo.end()]
			remo = search('\:[\s]+'+REGEX_FPNUM,tmp_str)
			tmp_str = header_str[remo.start():remo.end()]
			remo = search(REGEX_FPNUM,tmp_str)
			tau0 = float(tmp_str[remo.start():remo.end()])
			remo = search(regex_header_neqbw_tag+'\:[\s]+'+REGEX_FPNUM,header_str)
			tmp_str = header_str[remo.start():remo.end()]
			remo = search(REGEX_FPNUM,tmp_str)
			neqbw = float(tmp_str[remo.start():remo.end()])
			# select block substring
			block_str = adev_str[ri.end():]
			remo = search(regex_header,block_str)
			idx_block_end = None if not remo else remo.start()
			block_str = block_str[:idx_block_end]
			# parse block
			remo_iter_lines = finditer(regex_line,block_str)
			adev_block = {'tau':[],'adev':[],'err':[]}
			for rj in remo_iter_lines:
				line_str = block_str[rj.start():rj.end()]
				remo_iter_num = finditer(REGEX_FPNUM,line_str)
				for kk in range(3):
					rk = remo_iter_num.next()
					num_str = line_str[rk.start():rk.end()]
					adev_block[adev_block.keys()[kk]].append(float(num_str))
			adev_block['tau'] = array(adev_block['tau'])
			adev_block['adev'] = array(adev_block['adev'])
			adev_block['err'] = array(adev_block['err'])
			# create block dictionary
			this_block = {'TAU0':tau0,'NEQBW':neqbw,'adev':adev_block}
			# add block
			adev_blocks.append(this_block)
		
		return adev_blocks
	
	def _parse_fcounter(self,fcounter_str):
		unit_to_multiplier = {'m':1e-3,'k':1e3,'M':1e6,'G':1e9,'T':1e12, # all the usual suspects
								's':1.0,'H':1.0} # base units of interest in this method
		rv = {}
		# extract Reference Frequency
		remo = search('Reference[\s]+Frequency\:[\s]+[\d]+[\.[\d]*]?[\s]+[a-zA-Z]+',fcounter_str)
		ref_freq_str = fcounter_str[remo.start():remo.end()]
		remo = search('[\d]+[\.[\d]*]?',ref_freq_str)
		ref_freq = float(ref_freq_str[remo.start():remo.end()])
		remo = search('[mkMGT]?Hz',ref_freq_str)
		ref_unit = ref_freq_str[remo.start():remo.end()]
		ref_freq = ref_freq*unit_to_multiplier[ref_unit[0]]
		rv['ReferenceFrequency'] = {'value':ref_freq,'unit_str':ref_unit}
		
		# extract Avg Time unit
		remo = search('Avg[\s]+Time[\s]+\([a-zA-Z]+\)',fcounter_str)
		tmp = fcounter_str[remo.start():remo.end()]
		remo = search('\([a-zA-Z]+\)',tmp)
		tmp = tmp[remo.start():remo.end()]
		remo = search('[a-zA-Z]+',tmp)
		time_unit = tmp[remo.start():remo.end()]
		
		# extract Frequency unit
		remo = search('Frequency[\s]+\([a-zA-Z]+\)',fcounter_str)
		tmp = fcounter_str[remo.start():remo.end()]
		# this is end of header lines, so keep index to remo.end()
		idx_data = remo.end()
		remo = search('\([a-zA-Z]+\)',tmp)
		tmp = tmp[remo.start():remo.end()]
		remo = search('[a-zA-Z]+',tmp)
		freq_unit = tmp[remo.start():remo.end()]
		
		# extract data and build rest of return value
		dat = loadtxt(StringIO(fcounter_str[idx_data:]))
		rv['AvgTime'] = {'value':dat[:,0]*unit_to_multiplier[time_unit[0]],'unit_str':time_unit}
		rv['Frequency'] = {'value':dat[:,1]*unit_to_multiplier[freq_unit[0]],'unit_str':freq_unit}
		
		return rv
	
	# user-interface, get different things
	def get_adev(self):
		rv = self._show('ADEV')
		return self._parse_adev(rv)
	
	def get_fcounter(self):
		rv = self._show('FCOUNTER')
		return self._parse_fcounter(rv)
	
