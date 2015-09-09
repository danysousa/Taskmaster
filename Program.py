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
		self.stopAt = -1

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
		if ( self.getConfigValue("env") != None ) :
			for (key, value) in self.config["env"].items() :
				os.environ[str(key)] = str(value)
			return (os.environ)
		return (None)

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
		if ( len(self.process) != 0 ):
			print("This program is already started")
			return
		print("[Start to run " + self.name + "]")
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
									"restarted" : 0
								}
							)
			i += 1
		print("\t" + str(i) + " process launched")

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

	def stopTask(self):
		stopTime = self.getConfigValue("stoptime")

		if (stopTime == None or stopTime <= 0):
			self.stop(debug = True)
		else :
			if (stopTime < 0):
				stopTime = 0;
			print(self.name + " should be restart in " + str(stopTime) + " sec")
			self.stopAt = time.time() + stopTime

	# Stop all process
	def stop(self, debug = False):
		self.stopped = True
		if ( len(self.process) == 0 ):
			print("This program is already stopped")
			return
		if (debug == True):
			print( "[Start to kill " + self.name + "]" )
		self.getStopSignal()
		for (nb, elem) in enumerate(self.process) :
			if ( elem["process"].returncode == None ) :
				elem["process"].send_signal(self.getStopSignal())
			if (debug == True):
				print( "\t" + str(nb + 1) + "/" + str(len(self.process)) + " process killed")
		self.process = []

	def status(self) :
		progress = 0
		running = 0
		dead = 0

		print("[Status : " + self.name + "]")
		if ( len(self.process) == 0 ):
			print("\tProgram stopped")
			return
		for currentProcess in self.process :
			if ( currentProcess["process"].poll() == None ) :
				currentTime = time.time()
				if (currentTime - currentProcess["date"] >= self.config["starttime"]) :
					running += 1
				else :
					progress += 1
			else :
				dead += 1

		print("\t" + str(running) + " process running")
		print("\t" + str(dead) + " process dead")
		print("\t" + str(progress) + " process in progress")

	def update(self):
		i = 0;
		if (self.stopped == True):
			return
		if (self.stopAt > 0 and self.stopAt < time.time() ) :
			self.stop()
			return

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
		if ( autorestart == "always" ) :
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
		self.process[rank]["date"] = time.time()

	def reload( self, newConfig ) :
		restart = {
			"cmd" : self.config['cmd'] if 'cmd' in self.config else None,
			"umask" : self.config['umask'] if 'umask' in self.config else None,
			"workingdir" : self.config['workingdir'] if 'workingdir' in self.config else None,
			"stdout" : self.config['stdout'] if 'stdout' in self.config else None,
			"stderr" : self.config['stderr'] if 'stderr' in self.config else None,
			"env" :  self.config['env'] if 'env' in self.config else None
		}
		for (key, value) in restart.items() :
			if ( self.config["numprocs"] > newConfig["numprocs"]) :
				print ("flouflou")
				self.config = newConfig
				print ("Please restart " + self.name + " program")
				return ;
			elif ( self.config["numprocs"] < newConfig["numprocs"] ) :
				i = 0
				numberNewProcess = newConfig["numprocs"] - self.config["numprocs"];
				self.config = newConfig
				while ( i < numberNewProcess ) :
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
							"restarted" : 0
						}
					)
					i += 1
				return ;
			if key in newConfig :
				if ( newConfig[key] != value ) :
					self.config = newConfig
					print ("Please restart " + self.name + " program")
					return ;
			elif key in self.config :
				print(key)
				self.config = newConfig
				print ("Please restart " + self.name + " program 2.0")
				return ;
		self.config = newConfig
