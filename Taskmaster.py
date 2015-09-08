from Program import Program
import time
import sys
import getopt
import os
import threading

class Taskmaster(object):

	def __init__(self, prog):
		self.prog = prog
		self.updated = 0
		self.t = threading.Thread( name="start", target=self.start )
		self.t.start()
		self.updateAll()

	def restart():
		print("coucou")

	def start(self):
		while (1):
			sys.stdout.write("$> ")
			sys.stdout.flush()
			try:
				line = sys.stdin.readline()
				print(self.updated)
			except KeyboardInterrupt:
				break
			if not line:
				break
			time.sleep(0.05)

	def updateAll(self):
		while(1) :
			try:
				self.updated += 1
				time.sleep(0.05)
			except KeyboardInterrupt:
				break
