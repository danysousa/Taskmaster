import subprocess

class Program(object):

	def __init__(self, name, config):
		self.name = name
		self.config = config
		# print(name)

		if ( "autostart" in self.config and self.config["autostart"] == True ) :
			self.process = self.run()

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

	def run(self):
		process = subprocess.Popen(	self.getConfigValue("cmd"),
									shell=True,
									universal_newlines=True,
									stdout = self.getStdOut(),
									stderr = self.getStdErr())
