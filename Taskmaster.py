from Program import Program
import time
import json
import sys
import getopt
import os
import threading
import signal


class Taskmaster(object):

	def __init__(self, configFile):
		signal.signal(signal.SIGINT, self.quitBySignal)
		self.prog = self.load( configFile )
		self.updated = 0
		self.isDone = False;
		self.t = threading.Thread(name='shell', target=self.shell)

		self.t.start()
		self.updateAll()

	# Catch Ctrl+C Signal
	def quitBySignal(self, a, b):
		self.isDone = True
		print("Press return for quit")

	# Main Loop for command shell
	def shell(self):
		while ( self.isDone == False ):
			line = input("$>")
			self.checkLine(line)
			if ( line == "exit" ) :
				self.isDone = True
			if ( line == "status" ) :
				self.getStatus()


	# Main Loop for update && check Programs
	def updateAll(self):
		while ( self.isDone == False ):
			for (name, process) in self.prog.items():
				process.update()
			time.sleep(0.05)

	# Function for status command
	def getStatus(self) :
		for (key, value) in self.prog.items() :
			value.status()

	# Parse command line & select the associated function
	def checkLine(self, line):
		arg = line.split(" ")
		command = 	{
						"stop" : self.stopProgram,
						"restart" : self.restartProgram
					}

		if ( arg[0] in command ) :
			command[arg[0]](arg)

	# Function for stop command
	def stopProgram(self, arg):
		if ( len(arg) < 2 ):
			return

		if ( arg[1] in self.prog ) :
			self.prog[arg[1]].stop(debug = True)

	def restartProgram(self, arg):
		if ( len(arg) < 2 ):
			return
		if ( arg[1] in self.prog ) :
			self.prog[arg[1]].restartAll(debug = True)

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

