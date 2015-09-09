#!/usr/bin/python

import sys
import getopt
import os
import json
import signal

from pprint import pprint
from Program import Program
from Taskmaster import Taskmaster

# def showVariableEnv():
# 	for value in os.environ:
# 		print( value + " = " + os.environ[value] )
# 	print("---------------------")
# 	os.system( 'env | grep POK' )


def parsing( file ):
	with open(file) as data_file:
		data = json.load(data_file)

	return data

def main( argv ):
	if ( len( argv ) != 2 ):
		return

	# signal.pause()
	config = parsing(argv[1])
	program = {};
	for (key, value) in config.items():
		program[key] = Program(key, value)

	taskMaster = Taskmaster(program)

main( sys.argv )