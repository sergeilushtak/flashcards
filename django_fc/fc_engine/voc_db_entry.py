class VocDBEntry ():

	def from_ctxL_citL (self, ctxL, citL, date = ''):
		self.ctxs = '|'.join (ctxL)
		self.citL = citL

		lft_lemmaL = []
		rgt_lemmaL = []
		citstrL = []
		for cit in citL:
			if cit.lft_lemma != '':
				lft_lemmaL.append (cit.lft_lemma)
			if cit.rgt_lemma != '':
				rgt_lemmaL.append (cit.rgt_lemma)

			citstrL.append (cit.lft_usage + ' = ' + cit.rgt_usage)

		self.cits = '|'.join (citstrL)

		self.lft_lemma = '...'.join (lft_lemmaL)

		#------create lemma_ID
		rgt_sideL = []
		for w in rgt_lemmaL:
			w = w.split (';') [0]
			w = w.replace ('likely>', '').replace ('here>', '').strip ()
			rgt_sideL.append (w)
			
		self.lemma_ID  = '_'.join (lft_lemmaL) + '__' + '_'.join (rgt_sideL)
		#------end of create lemma_ID

		self.rgt_lemma = '...'.join (rgt_lemmaL)
		self.correct_answer = cit.lft_usage.lower ()

		self.date = date
		self.times_asked = 0
		self.ID = -1

	def is_correct (self, user_written_answer):
		return self.correct_answer == user_written_answer

	def get_correct_answer (self):
		return self.correct_answer

	def to_db_str (self):
		return '\t'.join ([str (self.ID), self.date, self.lemma_ID, self.lft_lemma, self.rgt_lemma, self.correct_answer, self.ctxs, self.cits, str (self.times_asked)])

	def from_db_str (self, db_str):
		(self.ID, self.date, self.lemma_ID, self.lft_lemma, self.rgt_lemma, self.correct_answer,
		self.ctxs, self.cits, self.times_asked) = db_str.split ('\t')
		self.times_asked = int (self.times_asked)
		self.ID = int (self.ID)

	def __str__ (self):

		ctxL = self.ctxs.split ('|')
		citL = self.cits.split ('|')
		strout = ctxL [0]
		for i in range (len (citL)):
			strout += '--- '+ citL [i] + ' ---'
			strout += ctxL [i + 1]
		strout += '\n'
		strout += 'lemma_ID : {}\n'.format (self.lemma_ID)
		strout += 'lft_lemma: {}\n'.format (self.lft_lemma)
		strout += 'rgt_lemma: {}\n'.format (self.rgt_lemma)
		strout += 'date     : {}\n'.format (self.date)
		strout += 'times_asked: {}\n'.format (self.times_asked)

		return strout


	def get_rgt_ctx_str (self):
		ctxL = self.ctxs.split ('|')
		citL = self.cits.split ('|')
		strout = ctxL [0]
		for i in range (len (citL)):
			rgt_usage = citL [i].split (' = ')[1]
			strout += '---' + rgt_usage + '---'
			strout += ctxL [i + 1]


		return strout

	def get_citL (self):
		return self.cits.split ('|')

	def get_ctxL (self):
		return self.ctxs.split ('|')

	def get_lft_ctx_str (self):
		ctxL = self.ctxs.split ('|')
		citL = self.cits.split ('|')
		strout = ctxL [0]
		for i in range (len (citL)):
			lft_usage = citL [i].split (' = ')[0]
			strout += '---' + lft_usage + '---'
			strout += ctxL [i + 1]

		return strout

	def copy (self):
		vdbe = VocDBEntry ()

		vdbe.rgt_lemma = self.rgt_lemma
		vdbe.lft_lemma = self.lft_lemma
		vdbe.lemma_ID = self.lemma_ID

		vdbe.citL = self.get_citL ().copy ()
		vdbe.cxtL = self.get_ctxL ().copy ()

		vdbe.date = self.date
		vdbe.times_asked = self.times_asked
