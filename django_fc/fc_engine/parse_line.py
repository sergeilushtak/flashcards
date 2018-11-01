from .voc_db_entry import VocDBEntry

LNK_CLOSED = -2
LNK_OPEN_UNDEFINED = -3
LNK_TO_CLOSEST = -1
LNK_TO_CLOSEST = -1

error_list = []

class InTxtCit ():

	def __init__ (self, lft_lemma, lft_usage, rgt_lemma, rgt_usage, lft_lnk, rgt_lnk, cittxt):

		self.lft_lemma = lft_lemma
		self.lft_usage = lft_usage
		self.rgt_lemma = rgt_lemma
		self.rgt_usage = rgt_usage
		self.lft_lnk = lft_lnk
		self.rgt_lnk = rgt_lnk
		self.cittxt = cittxt
		self.filler = ''

	def __str__ (self):
		return "\n".join ([
			  "cittxt   : {}".format (self.cittxt)
			, "lft_lemma: {}".format (self.lft_lemma)
			, "lft_usage: {}".format (self.lft_usage)
			, "rgt_lemma: {}".format (self.rgt_lemma)
			, "rgt_usage: {}".format (self.rgt_usage)
			, "lft_lnk  : {}".format (self.lft_lnk)
			, "rgt_lnk  : {}".format (self.rgt_lnk)
			, "filler   : {}".format (self.filler)

		])

def parse_cit (cittxt, lft_lnk, rgt_lnk):

	global error_list

	cittxt = cittxt.strip ().replace ('==', '=')
	spl_eq = cittxt.split ('=')

	if len (spl_eq) == 1:

			lft_lemma   = ''
			lft_usage = cittxt
			rgt_lemma = ''
			rgt_usage = ''

	elif len (spl_eq) == 2:

		(lft, rgt) = spl_eq

		part = lft
		spl_col = part.split (':')

		if len (spl_col) == 1:
			lemma = part.strip ()
			usage = lemma
		elif len (spl_col) == 2:

			usage, lemma = spl_col
			usage = usage.strip ()
			lemma = lemma.strip ()

		else:
			error_list.append ("parse_cit : [F] : found more than one \':\' in {}".format (part))
			return None

		(lft_usage, lft_lemma) = (usage, lemma)

		part = rgt
		spl_col = part.split (':')

		if len (spl_col) == 1:
			lemma = part.strip ()
			usage = lemma
		elif len (spl_col) == 2:

			lemma, usage = spl_col
			usage = usage.strip ()
			lemma = lemma.strip ()

		else:
			error_list.append  ("parse_cit : [F] : found more than one \':\' in {}".format (part))
			return None

		(rgt_usage, rgt_lemma) = (usage, lemma)

	else:
		error_list.append ("parse_cit : [F] : found more than one \'=\' in {}".format (cittxt))
		return None

	return InTxtCit (
		lft_lemma = lft_lemma
		, lft_usage = lft_usage
		, rgt_lemma = rgt_lemma
		, rgt_usage = rgt_usage
		, lft_lnk = lft_lnk
		, rgt_lnk = rgt_lnk
		, cittxt = cittxt
		)




# resolving links and figuring out how many entries the current line
# produces
def resolve_links (in_txt_citL):

	cit_indL = []
	rgt_lnkL = []
	group_noL = []

	unrlesolved_lft_lnk_cnt = 0

	LNK_RESOLVED = -111

	for c in in_txt_citL:
		rgt_lnkL.append (c.rgt_lnk)


	for ind in range (len (in_txt_citL)):
		c = in_txt_citL [ind]

		if c.lft_lnk == LNK_CLOSED:
			group_noL.append (len (cit_indL))
			cit_indL.append ([ind])

		else:

			for ii in range (ind - 1, -1, -1):
				if rgt_lnkL [ii] == c.lft_lnk:
					break

			if ii != -1:
#				print (ind)
#				print (cit_indL)
#				print (ii)
#				print (rgt_lnkL)
				cit_indL [group_noL [ii]].append (ind)
				rgt_lnkL [ii] = LNK_RESOLVED

				group_noL.append (ii)
#				print ('haha')
			else:
				#error
				unrlesolved_lft_lnk_cnt += 1
				# closing the left link
				group_noL.append (len (cit_indL))
				cit_indL.append ([ind])

	ii = 0
	while ii < len (cit_indL):
		if cit_indL:
			ii += 1
		else:
			cit_indL.pop (ii)

	unrlesolved_rgt_lnk_cnt = 0
	for rlnk in rgt_lnkL:
		#print (rlnk)
		if rlnk != LNK_RESOLVED and rlnk != LNK_CLOSED:
			#error
			unrlesolved_rgt_lnk_cnt += 1

	if unrlesolved_rgt_lnk_cnt + unrlesolved_lft_lnk_cnt > 0:
		print ("resolve_links : [W] : encountered {} unresloved links.".format (unrlesolved_rgt_lnk_cnt + unrlesolved_lft_lnk_cnt))
		print ("Among which:")
		if unrlesolved_lft_lnk_cnt > 0:
			print ("\t{} unresolved left link(s)".format (unrlesolved_lft_lnk_cnt))
		if unrlesolved_rgt_lnk_cnt > 0:
			print ("\t{} unresolved right link(s)".format (unrlesolved_rgt_lnk_cnt))

	return cit_indL



def create_voc_entry (citL, cit_indL, ctxL, date = ''):

	strout = ctxL [0]

	ctx_outL = []
	cit_outL = []

	for i in range (len (citL)):
		if i in cit_indL:
			ctx_outL.append (strout)
			cit_outL.append (citL [i])
			strout = ctxL [i + 1]

		else:
			strout += citL [i].filler
			strout += ctxL [i + 1]

	ctx_outL.append (strout)

	vdbe = VocDBEntry ()
	vdbe.from_ctxL_citL (ctx_outL, cit_outL, date)

	return vdbe


def line_to_vdbeL (line, date = ''):
	line = line.strip ()

	in_cit = False
	citstr = ''
	in_txt_citL = []
	ctxL = ['']


	for c in line:

		if in_cit:
			if c in '{[':
				print ("parse_line : [F] : found {} inside citation:\n\t{}".format (c, line))
			elif c in ']}':
				if c == ']':
					r_lnk = LNK_CLOSED
				else:
					if len (citstr) > 0 and citstr [-1].isdigit ():
						r_lnk = int (citstr [-1])
						citstr = citstr [:-1]
					else:
						r_lnk = LNK_TO_CLOSEST


				in_txt_cit = parse_cit (citstr, l_lnk, r_lnk)
				if in_txt_cit != None:
					in_txt_citL.append (in_txt_cit)

				citstr  = ''
				in_cit = False
				ctxL.append (c)

			else:
				if l_lnk == LNK_OPEN_UNDEFINED:
					assert (citstr == '')
					if c.isdigit():
						l_lnk = int (c)
						continue
					else:
						l_lnk = LNK_TO_CLOSEST

				citstr += c
				#print (citstr)
		else:
			if c in '}]':
				print ("parse_line : [F] : found {} outside citation:\n\t{}".format (c, line))
			elif c in '[{':
				if c == '[':
					l_lnk = LNK_CLOSED
				else:
					l_lnk = LNK_OPEN_UNDEFINED

				in_cit = True

				ctxL [-1] += c
				#print (ctxL [-1])
			else:
				ctxL [-1] += c
				#print (ctxL [-1])

	if in_cit:
		error_list.append ("parse_line : [F] : reached EOL while parsing citation:\n\t{}".format (line))
		return []


	"""
	for in_txt_cit in in_txt_citL:
		print (in_txt_cit)
		print ()

	for ctx in ctxL:
		print (ctx)
		print ()
	"""


	cit_indLL = resolve_links (in_txt_citL)

	#print ("cit_indLL:")
	#print (cit_indLL)

	# by convension citation groups without '=' in them mark those words/phrases whose
	# translation could not be found at this point, but which may be translated in the future.
	# These citations should obviously be ingored by Flashcards (treated as plain text).

	ii = 0
	while ii < len (cit_indLL):
		cit_indL = cit_indLL [ii]
		combined_rgt_lemma = ''

		for cit_ind in cit_indL:
			combined_rgt_lemma += in_txt_citL [cit_ind].rgt_lemma

		if combined_rgt_lemma == '':
			#no combined_rgt_lemma - ignore this cit group

			for ind in cit_indL:
				in_txt_citL [ind].filler = in_txt_citL [ind].cittxt
			#	ctxL [ind : ind + 2] = [ctxL [ind] + in_txt_citL [ind].cittxt + ctxL [ind + 1]]
				#in_txt_citL.pop (ind)

			cit_indLL.pop (ii)

		else:
			for ind in cit_indL:
				if in_txt_citL [ind].rgt_usage != '':
					in_txt_citL [ind].filler = in_txt_citL [ind].rgt_usage
				else:
					in_txt_citL [ind].filler = '..'

			ii += 1

#	ignore_untranslated (ctxL, in_txt_citL)

	# entry count == len (cit_indLL)

	vdbeL = []
	for ii in range (len (cit_indLL )):

		vdbe = create_voc_entry (in_txt_citL, cit_indLL [ii], ctxL, date)
		vdbeL.append (vdbe)


	return vdbeL


if __name__ == "__main__":
	line = "En ese momento crucial [se} le {resbaló:resbalarse=to slip:(it) slipped} la jeringa {de=out of] la mano y [aterrizó???] en un pedazo de suelo mojado al lado del [inodoro=toilet]."
	line = "E anche la Francia nutre seri dubbi. Pur dando il benvenuto alla finale ammissione dell'Arabia Saudita sull'uccisione del reporter, il ministro delle Finanze, Bruno Le Maire, sostiene che va fatta molta più luce di quanta se ne sia fatta [finora=so far]. "
	line = "Pieno sostegno al regno invece, arriva [sia=both} dall'Oman {che=and] dal Kuwait."

	print ()
	print (line)
	print ()

	vdbeL = line_to_vdbeL (line);


	line = "je [ne 1} l'a vu [bien=here> really] {1 guerre:ne...guerre = едва, barely:barely] [jamas???]."
	print (line)
	print ()
	vdbeL += line_to_vdbeL (line);

	for vdbe in vdbeL:
		print ('-----------------------------------------------')
		print (vdbe)
		print ()
		print ('\'reco\' mode answer: ')
		print ('\t>>>>>>>>>>>>>>>>>>>>>>')
		print ('\t>  '+ vdbe.lft_lemma_display + ' = ' + vdbe.rgt_lemma_display)
		print ('\t>')
		print ('\t>  '+ vdbe.get_rgt_ctx_str ())
		print ('\t>>>>>>>>>>>>>>>>>>>>>>')
		print ()
		print ('\'gen\' mode answer: ')
		print ('\t>>>>>>>>>>>>>>>>>>>>>>')
		print ('\t>  '+ vdbe.rgt_lemma_display + ' = ' + vdbe.lft_lemma_display)
		print ('\t>')
		print ('\t>  '+ vdbe.get_lft_ctx_str ())
		print ('\t>>>>>>>>>>>>>>>>>>>>>>')
		print ()
