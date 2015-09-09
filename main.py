import sys
import getopt
import os
import signal

from pprint import pprint
from Program import Program
from Taskmaster import Taskmaster

# def showVariableEnv():
# 	for value in os.environ:
# 		print( value + " = " + os.environ[value] )
# 	print("---------------------")
# 	os.system( 'env | grep POK' )


def main( argv ):
	if ( len( argv ) != 2 ):
		return

	# signal.pause()

	taskMaster = Taskmaster( argv[1] )

main( sys.argv )