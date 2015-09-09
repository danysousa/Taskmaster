from Program import Program
import time
import sys
import getopt
import os
import threading
import signal


class Taskmaster(object):

	def __init__(self, prog):
		signal.signal(signal.SIGINT, self.quitBySignal)
		self.prog = prog
		self.isDone = False;
		self.t = threading.Thread(name='shell', target=self.shell)
		self.t.start()
		self.updateAll()

	def quitBySignal(self, a, b):
		self.isDone = True
		print("Press return for quit")

	def shell(self):
		while ( self.isDone == False ):
			line = input("$>")
			if ( line == "exit" ) :
				self.isDone = True
			if ( line == "stop cat"):
				self.prog["cat"].stop(debug = True)
			if ( line == "status" ) :
				self.getStatus()

	def updateAll(self):
		while ( self.isDone == False ):
			time.sleep(0.05)

	def getStatus(self) :
		for (key, value) in self.prog.items() :
			value.status()
