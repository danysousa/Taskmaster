import sys
import getopt
import os

class Program(object):

	def __init__(self, name, config):
		self.name = name
		self.config = config
		# print(name)

		# if ( "autostart" in self.config and self.config["autostart"] == True ) :
		# 	print("YOLO")
		# else :
		# 	print(self.config["autostart"])

	def getEnv(self) :
		for (key, value) in self.config["env"].items() :
			os.environ[str(key)] = str(value)
