class Settings ():

	class Chunk ():
		pass
	class Session ():
		pass

	class Lessons ():
		pass

	class Voc ():
		pass

	# default settings
	session = Session ()
	session.rhn_initial = 1
	session.rhn_punitive = 2
	session.mode = 'reco'

	lessons = Lessons ()
	lessons.new_words = 12
	lessons.review = 12
	lessons.window = 72

	lessons.rand_old = 20


	chunk = Chunk ()
	chunk.size = 12

	voc = Voc ()
	voc.frequency = 1



	def __init__ (self):
		self.db_id = -1
		self.session = Settings.Session ()
		self.chunk = Settings.Chunk ()
		self.lessons = Settings.Lessons ()
		self.voc = Settings.Voc ()


		self.session.rhn_initial = Settings.session.rhn_initial
		self.session.rhn_punitive = Settings.session.rhn_punitive
		self.session.mode = Settings.session.mode

		self.lessons.new_words = Settings.lessons.new_words
		self.lessons.review = Settings.lessons.review
		self.lessons.window = Settings.lessons.window
		self.lessons.rand_old = Settings.lessons.rand_old


		self.chunk.size = Settings.chunk.size

		self.voc.frequency = Settings.voc.frequency

	def to_json (self):
		return {
			'db_id' 		: self.db_id,
			'chunk.size' 	: self.chunk.size,
			'voc.frequency' : self.voc.frequency,
			'session.rhn_initial' 	: self.session.rhn_initial,
			'session.rhn_punitive'	: self.session.rhn_punitive,
			'session.mode' 			: self.session.mode,
		}

	def from_json (self, jo):
		self.ib_id 			= jo ['db_id']
		self.chunk.size 	= jo ['chunk.size']
		self.voc.frequency	= jo ['voc.frequency']
		self.session.rhn_initial 	= jo ['session.rhn_initial']
		self.session.rhn_punitive	= jo ['session.rhn_punitive']
		self.session.mode 			= jo ['session.mode']
