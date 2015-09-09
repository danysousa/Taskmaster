import sys
import getopt
import os
import subprocess
import time
import errno

def pre_exec(config) :
	os.umask( int( config["umask"], 8 ))

class Program(object):

	def __init__(self, name, config):
		self.name = name
		self.config = config
		self.process = []
		self.currentRetries = 0
		self.stopped = False

		if ( "autostart" in self.config and self.config["autostart"] == True ) :
			self.run()

	# Return the fd for redirect stdout
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

	# Return the fd for redirect stderr
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

	# Return the config value for key
	def getConfigValue(self, key) :
		if ( key in self.config ) :
			return ( self.config[key] )
		else :
			return ( None )

	# Return the env of process
	def getEnv(self) :
		for (key, value) in self.config["env"].items() :
			os.environ[str(key)] = str(value)
		return (os.environ)

	# Return the working dir of process
	def getWorkingDir(self):
		if ( "workingdir" in self.config and self.config["workingdir"] != "" ) :
			return ( self.config["workingdir"] )
		else :
			return ( None )

	# Launch numprocs process and complete self.process
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
									"name" : self.name + " " + str(i + 1),
									"restarted" : 0
								}
							)
			i += 1

	# Return the signum for stop process
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
		self.stopped = True
		if (debug == True):
			print( "[Start to kill " + self.name + "]" )
		self.getStopSignal()
		for (nb, elem) in enumerate(self.process) :
			if ( elem["process"].returncode == None ) :
				elem["process"].send_signal(self.getStopSignal())
			if (debug == True):
				print( "\t" + str(nb + 1) + "/" + str(len(self.process)) + " process killed")

	def status(self) :
		for currentProcess in self.process :
			if ( currentProcess["process"].poll() == None ) :
				print(currentProcess["name"] + " running ")
			else :
				print(currentProcess["name"] + " not running ")

	def update(self):
		i = 0;
		while (i < len(self.process)) :
			if ( self.process[i]["process"].poll() != None ) :
				self.checkRestart(i)
			i += 1

	def checkRestart(self, rank):
		if ( self.process[rank]["process"].returncode == None or self.stopped == True ) :
			return

		autorestart = self.getConfigValue("autorestart")
		if (autorestart == "never") :
			return

		exitcodes = self.getConfigValue("exitcodes")
		startretries = self.getConfigValue("startretries")
		if ( startretries <= self.process[rank]["restarted"]) :
			return
		if ( autorestart == "ever" ) :
			self.process[rank]["restarted"] += 1
			self.restart(rank)
			return

		for code in exitcodes:
			if ( code == self.process[rank]["process"].returncode ) :
				return
			self.process[rank]["restarted"] += 1

		self.restart(rank)

	def restartAll(self, debug = False):
		if (debug == True):
			print( "[Start to restart " + self.name + "]" )

		i = 0
		while ( i < len(self.process) ):
			self.restart(i)
			if (debug == True):
				print( "\t" + str(i + 1) + "/" + str(len(self.process)) + " process restarted")
			i += 1

	def restart(self, rank):
		if ( self.process[rank]["process"].returncode == None ):
			self.process[rank]["process"].send_signal(self.getStopSignal())
		self.process[rank]["process"] = subprocess.Popen( self.getConfigValue("cmd"),
															shell=True,
															universal_newlines=True,
															stdout = self.getStdOut(),
															stderr = self.getStdErr(),
															cwd=self.getWorkingDir(),
															preexec_fn = pre_exec(self.config),
															env = self.getEnv()
														)