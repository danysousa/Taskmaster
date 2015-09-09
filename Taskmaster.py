from Program import Program
import time
import json
import sys
import getopt
import os
import threading
import signal
from Shell import Shell


class Taskmaster(object):

	def __init__(self, configFile):
		signal.signal(signal.SIGINT, self.quitBySignal)
		self.prog = self.load( configFile )
		self.updated = 0
		self.isDone = False;
		self.shell = Shell(self)
		self.t = threading.Thread(name='shell', target=self.shell.cmdloop)

		self.t.start()
		self.updateAll()

	# Catch Ctrl+C Signal
	def quitBySignal(self, a, b):
		return True

	# Main Loop for update && check Programs
	def updateAll(self):
		while ( self.isDone == False ):
			for (name, process) in self.prog.items():
				process.update()
			time.sleep(0.05)

	# Parse Json config file
	def parsing(self, configFile ):
		with open(configFile) as data_file:
			data = json.load(data_file)
		return data

	# Load config file
	def load(self, configFile) :
		config = self.parsing( configFile )
		program = {};
		for (key, value) in config.items():
			program[key] = Program(key, value)
		return program;

