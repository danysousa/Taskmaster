import sys
import getopt
import os
import subprocess
import time

def pre_exec(config) :
	os.umask( int( config["umask"], 8 ))

class Program(object):

	def __init__(self, name, config):
		self.name = name
		self.config = config
		self.process = [];
		self.currentRetries = 0;

		if ( "autostart" in self.config and self.config["autostart"] == True ) :
			self.run()

	def getStdOut(self) :
		if ( "stdout" in self.config and self.config["stdout"] != "" ) :
			fd = open(self.config["stdout"], 'a')
			if ( fd == -1 ) :
				print("[Warning] Can't open specify stdout file for " + self.name)
				return ( subprocess.PIPE )
			else :
				return ( fd )
		else :
			return ( subprocess.PIPE )

	def getStdErr(self) :
		if ( "stderr" in self.config and self.config["stderr"] != "" ) :
			fd = open(self.config["stderr"], 'a')
			if ( fd == -1 ) :
				print("[Warning] Can't open specify stderr file for " + self.name)
				return ( subprocess.PIPE )
			else :
				return ( fd )
		else :
			return ( subprocess.PIPE )

	def getConfigValue(self, key) :
		if ( key in self.config ) :
			return ( self.config[key] )
		else :
			return ( None )

	def getEnv(self) :
		for (key, value) in self.config["env"].items() :
			os.environ[str(key)] = str(value)
		return (os.environ)

	def getWorkingDir(self):
		if ( "workingdir" in self.config and self.config["workingdir"] != "" ) :
			return ( self.config["workingdir"] )
		else :
			return ( None )

	def run(self):
		nbProcess = self.getConfigValue("numprocs")
		i = 0;

		if ( nbProcess == None ):
			nbProcess = 1
		while ( i < nbProcess ):
			self.process.append( {	"process" : subprocess.Popen( self.getConfigValue("cmd"),
												shell=True,
												universal_newlines=True,
												stdout = self.getStdOut(),
												stderr = self.getStdErr(),
												cwd=self.getWorkingDir(),
												preexec_fn = pre_exec(self.config),
												env = self.getEnv()
												),
									"date" : time.time(),
									"name" : self.name + " " + str(i + 1)
								}
							)
			i += 1

	# Return the signum with
	def getStopSignal(self):
		signame = self.getConfigValue("stopsignal")

		if ( signame == None ) :
			return (9)

		i = 0;
		sig = ["HUP", "INT", "QUIT", "ILL", "TRAP", "ABRT", "EMT", "FPE", "KILL", "BUS", "SEGV", "SYS", "PIPE", "ALRM", "TERM", "URG", "STOP", "TSTP", "CONT", "CHLD", "TTIN", "TTOU", "IO", "XCPU", "XFSZ", "VTALR", "PROF", "WINCH", "INFO", "USR1", "USR2"]
		while i < len(sig) :
			if sig[i] == signame:
				return (i + 1)
			i += 1
		return (9)

	# Stop all process
	def stop(self, debug = False):
		if (debug == True):
			print( "[Start to kill " + self.name + "]" )
		self.getStopSignal()
		for (nb, elem) in enumerate(self.process) :
			elem["process"].send_signal(self.getStopSignal())
			if (debug == True):
				print( "\t" + str(nb + 1) + "/" + str(len(self.process)) + " process killed")

	def is_process_running(self, process_id):
		try:
			os.kill(process_id, 0)
			return True
		except OSError:
			return False

	def status(self) :
		for currentProcess in self.process :
			print(currentProcess["process"].pid)
			if ( self.is_process_running( currentProcess["process"].pid ) == True ) :
				print(currentProcess["name"] + " is alive ")
			else :
				print(currentProcess["name"] + " is dead ")
