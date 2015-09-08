from Program import Program
import time
import sys


class Taskmaster(object):

	def __init__(self, prog):
		self.prog = prog
		self.start()

	def start(self):
		isDone = False
		while ( isDone == False ):
			time.sleep(0.05)