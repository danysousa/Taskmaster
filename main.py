import sys
import getopt
import os
import json
from pprint import pprint

def variableEnvExist( name ):
	for value in os.environ:
		if ( name == value ):
			return ( 1 )
	return ( 0 )

def setVariableEnv( name, value ):
	if ( variableEnvExist( name ) == 1 ):
		os.environ[name] = os.environ[name] + value
	else:
		os.environ[name] = value;

def showVariableEnv():
	for value in os.environ:
		print( value + " = " + os.environ[value] )
	print("---------------------")
	os.system( 'env | grep POK' )

def getNextLine( file ):
	f = open( argv[1], 'r' )
	lignes  = f.readlines()
	f.close()

	for ligne in lignes:
		print( ligne )

def parsing( file ):
	with open(file) as data_file:
		data = json.load(data_file)

	print(data["glossary"]["title"])

def main( argv ):
	if ( len( argv ) == 2 ):
		parsing(argv[1])
		# setVariableEnv( "POK", "POUUUKKY POUUUKY");
		# showVariableEnv()

		# os.umask( 0o700 )
		# fh1 = os.open( "qq1.junk", os.O_CREAT, 0o777 )
		# os.close ( fh1 )

		sys.exit( 0 );

main( sys.argv )