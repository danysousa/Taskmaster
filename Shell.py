import cmd
import Taskmaster
import signal

class Shell(cmd.Cmd):

	"""docstring for Shell"""
	def __init__(self, taskmaster):
		super(Shell, self).__init__()
		signal.signal(signal.SIGINT, self.sig)
		self.prompt = "$>"
		self.taskmaster = taskmaster

	def sig(self, a, b):
		self.onecmd("    \n")

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
		Restart the program"""
		for (key, value) in self.taskmaster.prog.items() :
			value.status()

	def do_exit(self, line) :
		self.taskmaster.isDone = True
		exit()
