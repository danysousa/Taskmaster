import cmd
import Taskmaster
import signal
from Program import Program

class Shell(cmd.Cmd):

	"""docstring for Shell"""
	def __init__(self, taskmaster):
		super(Shell, self).__init__()
		signal.signal(signal.SIGINT, self.sig)
		self.prompt = "$>"
		self.taskmaster = taskmaster

	def sig(self, a, b):
		self.onecmd("\n")

	def emptyline(self):
		return True

	# Function for stop command
	def do_stop(self, program):
		"""stop [program]
		Stop the program"""

		if ( program == None or program == "" ):
			print( "Usage: stop [program]" )
		if ( program in self.taskmaster.prog ) :
			self.taskmaster.prog[program].stopTask()

	# Function for start command
	def do_start(self, program):
		"""start [program]
		Start the program"""

		if ( program == None or program == "" ):
			print( "Usage: start [program]" )
		if ( program in self.taskmaster.prog ) :
			self.taskmaster.prog[program].run()

	def do_restart(self, program):
		"""restart [program]
		Restart the program"""

		if ( program == None or program == "" ):
			print( "Usage: restart [program]" )
		if ( program in self.taskmaster.prog ) :
			self.taskmaster.prog[program].restartAll(debug = True)


	# Function for status command
	def do_status(self, line) :
		"""status
		Print status for all programs"""
		for (key, value) in self.taskmaster.prog.items() :
			value.status()

	def do_exit(self, line) :
		"""exit
		Exit the main program"""
		self.taskmaster.isDone = True
		exit()

	def do_reload(self, line) :
		"""reload
		Reload the config file and apply change"""
		config = self.taskmaster.parsing( )
		if ( len(config) < len(self.taskmaster.prog) ) :
			for (key, value) in self.taskmaster.prog.items() :
				if key not in config :
					self.taskmaster.prog[key].stop()
		else :
			for (key, value) in config.items() :
				if key not in self.taskmaster.prog :
					self.taskmaster.prog[key] = Program(key, config)
			# 	if key not in self.taskmaster.prog :
			# 	self.taskmaster.prog[key].start()
		for (key, value) in config.items() :
			self.taskmaster.prog[key].reload( value )
