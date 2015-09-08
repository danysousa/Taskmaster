import sys
import getopt
import os
import json
from pprint import pprint
from Program import Program

def showVariableEnv():
	for value in os.environ:
		print( value + " = " + os.environ[value] )
	print("---------------------")
	os.system( 'env | grep POK' )

def parsing( file ):
	with open(file) as data_file:
		data = json.load(data_file)

	return data

def main( argv ):
	if ( len( argv ) != 2 ):
		return

	config = parsing(argv[1])
	program = {};
	for (key, value) in config.items():
		program[key] = Program(key, value)
		program[key].getEnv()

	# os.umask( 0o700 )
	# fh1 = os.open( "qq1.junk", os.O_CREAT, 0o777 )
	# os.close ( fh1 )


main( sys.argv )