import codecs
from collections import defaultdict
from .parse_line import line_to_vdbeL
from .voc_db_entry import VocDBEntry
import sys
def break_up_in_sentences (line):
	in_cit = False
	line = line.replace ('(.)', 'par_dot_par')
	line = line.replace ('(?)', 'par_ques_par')
	line = line.replace ('(!)', 'par_excl_par')
	line = line.replace ('...', 'dot_dot_dot')
	sentenceL = []
	sentence = ''

	for c in line:

		sentence += c
		if in_cit:
			if c in ']}':
				in_cit = False
		else:
			if c in '{[':
				in_cit = True
			else:
				if c in '!.?':
					sentenceL.append (sentence)
					sentence = ''
	if sentence != '':
		sentenceL.append (sentence)


	for ii in range (len (sentenceL)):
		sentenceL [ii] = sentenceL [ii].replace ('par_dot_par', '(.)')
		sentenceL [ii] = sentenceL [ii].replace ('par_ques_par', '(?)')
		sentenceL [ii] = sentenceL [ii].replace ('par_excl_par', '(!)')
		sentenceL [ii] = sentenceL [ii].replace ('dot_dot_dot', '...')

	return sentenceL





class  dbVoc ():

	def __init__ (self):
		self.id2vdbe = dict ()
		self.date2idL = defaultdict (list)
		self.dateL = []

		self.is_complete = False
		self.max_times_asked = 0

	def from_txt_file (self, file_txt):
		# read the text file with citations

		self.id2vdbe = dict ()

		date = ''
		index = 0
		with codecs.open (file_txt, 'r', 'utf-8-sig') as fin:
			for line in fin :
				line= line.strip ()
				if line.startswith ('date:'):
					date = line.split (':') [1].strip ().lower ()
					#print (date)
				else:
					for vdbe in line_to_vdbeL (line, date):
						self.id2vdbe [index] = vdbe
						index += 1

		self.max_times_asked = 0

		self.complete ()

	def from_uploaded_file (self, uploaded_file):
			# read the text file with citations

		self.id2vdbe = dict ()

		date = ''
		index = 0
		utf8_text = uploaded_file.read ().decode ('utf-8')
		self.from_text (utf8_text)

	def from_text (self, txt):
			# read the text file with citations

		self.id2vdbe = dict ()

		date = ''
		index = 0
		lineL = txt.split ('\n')

		for line in lineL :
#			line= str (line.strip ()
			line = line.strip ()
			if line == "":
				continue

			spl = line.split (':')
			#print (spl)
			if len (spl) > 1 and spl [0].strip ().lower () == 'date':
				date = ':'.join (spl [1:]).strip ().lower ()
				#print ("===========================")
				#print ("date: " + date)
				#print ("===========================")
			else:
				sentenceL = break_up_in_sentences (line)

				#sentenceL = [line]
				for sentence in sentenceL:
					for vdbe in line_to_vdbeL (sentence, date):
						self.id2vdbe [index] = vdbe
						vdbe.ID = index
						index += 1

		self.max_times_asked = 0

		self.complete ()


	def from_db_file (self, file_db):

		self.id2vdbe = []

		self. max_times_asked = 0

		with codecs.open (file_db, 'r', 'utf-8-sig') as fin:
			for line in fin :
				vdbe = VocDBEntry ()
				vdbe.from_db_str (line.strip ())


				self.id2vdbe [vdbe.ID] = vdbe

				if vdbe.times_asked > self.max_times_asked:
					self.max_times_asked = vdbe.times_asked

		self.complete ()

	def add_entry (self, vdbe):
		self.id2vdbe [vdbe.ID] = vdbe

		if vdbe.times_asked > self.max_times_asked:
			self.max_times_asked = vdbe.times_asked

		if vdbe.date not in self.date2idL:
			self.dateL.append (vdbe.date)

		self.date2idL [vdbe.date].append (vdbe.ID)

	def complete (self):
		self.make_dateL ()
		self.make_date2idL ()
		self.max_times_asked = 0
		for _, vdbe in self.id2vdbe.items ():
			if self.max_times_asked < vdbe.times_asked:
				self.max_times_asked = vdbe.times_asked

		self.is_complete = True

	def make_dateL (self):

		self.dateL = []
		dateS = set ()
		for _,vdbe in self.id2vdbe.items ():
			date = vdbe.date
			if date not in dateS:
				self.dateL.append (vdbe.date)
				dateS.add (date)


	def make_date2idL (self):

		self.date2idL = defaultdict (list)
		for id, vdbe in self.id2vdbe.items ():
			self.date2idL [vdbe.date].append (vdbe.ID)


	def date_append (self, db):

		if not self.is_complete :
			self.complete ()

		if not db.is_complete :
			db.complete ()


		for date in self.dateL:
			if date not in self.date2idL:
				self.dateL.append (date)
				self.date2idL [date] = db.date2idL [date]
				for id in db.date2idL [date]:
					self.id2vdbe [id] += db.id2vdbe [id]


	def to_db_file (self, file_db):
		with codecs.open (file_db, 'w', 'utf-8-sig') as fout:
				id__vdbe_L = sorted (self.id2vdbe.items ())
				for _, vdbe in id__vdbe_L:
					fout.write (vdbe.to_db_str () + '\n')



	def record_processed (self, ids):
		for id in ids:
			self.id2vdbe [id].times_asked += 1
			if self.max_times_asked < self.id2vdbe [id].times_asked:
				self.max_times_asked = self.id2vdbe [id].times_asked


	def get_entry_likelihood (self, id):
		return self.max_times_asked - self.id2vdbe [id].times_asked + 1

	def	get_intervalled_idL (self, start, size):
		idL = list (self.id2vdbe.keys ())
		idL.sort ()
		return idL [start:start + size]


	def get_dated_idL (self, date):
			try:
				return self.date2idL [date]
			except:
				return []

	def get_dated_idL_given_date_ind (self, date_ind):

		if type (date_ind) is tuple :
			from_ind = date_ind [0]
			to_ind   = date_ind [1]
			print ("mydebug >>> db_voc.get_dated_idL_given_date_ind : indices : {}, {}".format (from_ind, to_ind))
			try:
				lst = self.dateL [from_ind: to_ind]
			except:
				return []
		else:
			print ("mydebug >>> db_voc.get_dated_idL_given_date_ind : index : {}".format (date_ind))
			try :
				lst = [self.dateL [date_ind]]
			except:
				return []

		idL = []
		for date in lst:
			print ("mydebug >>> db_voc.get_dated_idL_given_date_ind : date : {}".format (date))
			idL += self.date2idL [date]

		return idL

	def get_date_cnt (self):
		return len (self.dateL)

	def get_dateL (self):
		return self.dateL

	def db_insert (self, vdbe):
		self.id2vdbe [vdbe.ID] = vdbe
		self.is_complete = False

	def get_voc_entry (self, ID):
		return self.id2vdbe [ID]

	def get_size (self):
		return len (self.id2vdbe)

	def get_idL (self):
		idL = []
		for id in self.id2vdbe:
			idL.append (id)
		idL.sort ()

		#print ("mydebug >>> dbVoc.get_idL () : {}".format (str (idL)))

		return idL

	def __len__ (self):
		return len (self.id2vdbe)


	def to_json (self):
		id2vdbe_json = dict ()
		for id, vdbe in self.id2vdbe.items ():
			id2vdbe_json [id] = vdbe.to_db_str ()

		return {
			'id2vdbe' : id2vdbe_json
			, 'dateL' : self.dateL
			, 'date2idL' : self.date2idL
			, 'max_times_asked' : self.max_times_asked
			, 'is_complete' : self.is_complete
		}

	def from_json (self, json_obj):
		self.dateL = json_obj ['dateL']
		self.date2idL = json_obj ['date2idL']
		self.max_times_asked = json_obj ['max_times_asked']
		self.is_complete = json_obj ['is_complete']

		self.id2vdbe = dict ()
		for id, vdbe_json in json_obj ['id2vdbe'].items ():
			vdbe = VocDBEntry ()
			vdbe.from_db_str (vdbe_json)
			self.id2vdbe [id] = vdbe


if __name__ == '__main__':

	import os.path

	USAGE = '\n\t'.join ([
			'Usage'
			, 'python ' + sys.argv [0] + ' file_txt  file_db  [-da for append mode, default: file_db will be overwritten]'
		])

	try:
		ii = 1
		file_txt = sys.argv [ii]; ii += 1
		file_db = sys.argv [ii]; ii += 1
	except :
		print
		print (USAGE)
		print
		exit


	overwrite = False
	if len (sys.argv) > 3:
		if sys.argv [3] == '-ovr':
			overwrite = True

	db_new = dbVoc ()
	db_new.from_txt_file (file_txt)

	if not overwrite and os.path.isfile (file_db):
		db = dbVoc ()
		db.from_db_file (file_db)
		db.date_append (db_new)
		db.to_db_file (file_db)

	else:
		if os.path.isfile (file_db):
			rsp = input ('Are you sure you want to over write an existing {} [y/n]?'.format (file_db))
			if rsp.strip ().lower () != 'y':
				exit ()

		db_new.to_db_file (file_db)
