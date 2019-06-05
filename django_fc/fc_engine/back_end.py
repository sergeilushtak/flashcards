
from random import randint
from random import shuffle
from random import sample

from fc_engine import messages

class FCEntry ():
	def new (self, rhn, vocID):
		self.ID = vocID
		self.rhn = rhn
		self.shots = 0
		self.hits = 0
		self.prob = 0

	def is_live (self):
		return self.rhn > 0
	def __str__ (self):
		return "ID: {}, rhn: {}, prob {}".format (self.ID, self.rhn, self.prob)

	def copy (self):
		fce = FCEntry ()
		fce.shots = self.shots
		fce.hits = self.hits
		fce.ID = self.ID
		fce.rhn = self.rhn
		fce.prob = self.prob

		return fce

	def to_json (self):
		return {
			'ID'    : self.ID,
			'rhn'   : self.rhn,
			'shots' : self.shots,
			'hits'  : self.hits,
			'prob'  : self.prob,
		}

	def from_json (self, jo):
		self.ID    = jo ['ID']
		self.rhn   = jo ['rhn']
		self.shots = jo ['shots']
		self.hits  = jo ['hits']
		self.prob  = jo ['prob']


class state_of_affairs ():

	def new (self, ss):
		self.cur_entry_ind = ss.cur_entry_ind 					# cur entry index in session.live_entryL
		self.cur_entry_copy = ss._entry_pool [ss.cur_entry_ind].copy ()  		# cur entry snapshot

		self.live_entryL_copy = ss.live_entryL.copy ()
		self.dead_entryS_copy = ss.dead_entryS.copy ()

	def to_json (self):

		return {
			  'cur_entry_ind'   : self.cur_entry_ind
			, 'cur_entry_copy'  : self.cur_entry_copy.to_json ()
			, 'live_entryL_copy'  : self.live_entryL_copy
			, 'dead_entryL_copy'  : list (self.dead_entryS_copy)
		}

	def from_json (self, j_obj):
		self.cur_entry_ind   = j_obj ['cur_entry_ind']

		self.cur_entry_copy  = FCEntry ()
		self.cur_entry_copy.from_json (j_obj ['cur_entry_copy'])


		self.live_entryL_copy = j_obj ['live_entryL_copy']
		self.dead_entryS_copy = set (j_obj ['dead_entryL_copy'])




class session ():

	MAX_SAVED_STATE_NUMBER = 12

	def __init__ (self):
		self._entry_pool = []
		self.live_entryL = []
		self.dead_entryS = set ()
		self.running = False


	def start (self, stt, voc, idL, session_size = 0):

		if len (idL) == 0:
			return False
		print ('mydebug>>> Session.start : the session has started. session_size = {}, len(idL) = {}'.format (session_size, len (idL)))

		self.register_dead ()

		#self.settings = settings

		self._entry_pool = []

		if session_size == 0 or session_size >= len (idL):
			for ii in range (len (idL)):

				## voc [ii] is dict { <mode> : VocCacheEntry }

				ID = idL[ii]
				fce = FCEntry ()
				fce.new (stt.session.rhn_initial, ID)
				self._entry_pool.append (fce)

			if stt.session.randomize:
				shuffle (self._entry_pool)

			print ('Session.start session _ size = {}'.format (len (self._entry_pool)))
			"""
			for fce in self._entry_pool :
				print (fce)
				break
			"""
		else:    #session size is less than entry pull size (voc). Choose entries rundomly

			likelihoodL = list ()

			random_pool_size = 0
			for ii in range (len (idL)):
				likelihoodL.append (voc.get_entry_likelihood (idL[ii]))
				random_pool_size += likelihoodL [-1]

			idL = idL.copy () #this list shall be modified - don't want to affect the input param idL

			for ii in range (session_size):

				#ind = randint (0, len (voc_clone))

				iii = randint (1, random_pool_size)
				s = 0
				for ind in range (len (likelihoodL)):
					s += likelihoodL [ind]
					if s > iii:
						break

				fce = FCEntry ()
				fce.new (stt.session.rhn_initial, idL[ind])
				self._entry_pool.append (fce)

				idL.pop (ind)
				random_pool_size -= likelihoodL [ind]
				likelihoodL.pop (ind)


		self.initial_rhn = stt.session.rhn_initial
		self.punitive_rhn = stt.session.rhn_punitive

		self.live_entryL = list (range (len (self._entry_pool)))
		self.cur_entry_ind = self.live_entryL .pop (0)

		print ("mydebug >>>>  Session.start live_entryL = {}".format (self.live_entryL))
		self.dead_entryS = set ()

		self.running = True

		self.state_stack = []
		self.state_sp = 0

		return True

	def to_json (self):
		for fce in self._entry_pool:
			print (fce)
			break

		_entry_pool = [entry.to_json () for entry in self._entry_pool]
		state_stack = [state.to_json () for state in self.state_stack]
		return {
			"_entry_pool"  : _entry_pool,
			"live_entryL"  : self.live_entryL,
			"dead_entryL"  : list (self.dead_entryS),
			"running"      : self.running,
			"punitive_rhn" : self.punitive_rhn,
			"initial_rhn"  : self.initial_rhn,
			"state_stack"  : state_stack,
			"state_sp"     : self.state_sp,
			"cur_entry_ind" : self.cur_entry_ind
		}

	def from_json (self, jo):
		self.running        = jo ['running']
		self.punitive_rhn   = jo ['punitive_rhn']
		self.initial_rhn    = jo ['initial_rhn']
		self.state_sp       = jo ['state_sp']


		self._entry_pool = []
		for jentry in jo ['_entry_pool']:
			fce = FCEntry  ()
			fce.from_json (jentry)
			self._entry_pool.append (fce)

		self.dead_entryS = set (jo ['dead_entryL'])
		self.live_entryL = jo ['live_entryL']


		self.state_stack = []
		for jstate in jo ['state_stack']:
			st = state_of_affairs ()
			st.from_json (jstate)
			self.state_stack.append (st)

		self.cur_entry_ind = jo ['cur_entry_ind']



	def register_dead (self):
		if len (self.dead_entryS) > 0:
			idS = set ()
			for ind in self.dead_entryS:
				fce = self._entry_pool [ind]
				idS.add (fce.ID)
			#print ("back_end.Session.register_dead : idS : {}".format (idS))
			messages.send (to_whom = 'engine', what = 'record_processed', data = idS )

	def restart (self):
		for fce in self._entry_pool:
			fce.rhn = self.initial_rhn
			fce.shots = 0
			fce.hits = 0

		self.live_entryL = list (range (len (self._entry_pool)))
		print ("mydebug >>>>  Session.restart live_entryL = {}".format (self.live_entryL))
		self.dead_entryS = set ()

		self.running = True

		self.cur_entry_ind = self.live_entryL. pop (0)

		self.state_stack = []
		self.state_sp = 0

		return True

	def resume (self):
		self.running = True
		self.cur_entry_ind = self.live_entryL. pop (0)

	def get_live_IDs (self):
		return [self._entry_pool [ind].ID for ind in self.live_entryL]


	def __len__ (self):
		return len (self.live_entryL) + 1 # current entry index is not in live_entryL

	def save_state (self):
		self.state_stack = self.state_stack [:self.state_sp]
		state = state_of_affairs ()
		state.new (self)

		self.state_stack.append (state)

		if self.state_sp == session.MAX_SAVED_STATE_NUMBER:
			self.state_stack.pop (0)
		else:
			self.state_sp += 1
		#print (self.state_stack)
		#print (self.state_sp)

	def roll_back (self):
		if self.state_sp > 0:
			if self.state_sp == len (self.state_stack):
				self.save_state ()
				self.state_sp -= 1

			self.state_sp -= 1
			self.restore_state ()

	def roll_forward (self):
		if self.state_sp < len (self.state_stack) - 1:
			self.state_sp += 1
			self.restore_state ()

	def restore_state (self):

		# print ("restoring state")
		# i = 0
		# for st in self.state_stack:
		# 	print ('{}{}'.format (i, st.cur_entry_copy))
		# 	i += 1
		# print ("looking at state [{}] = {}".format (self.state_sp, self.state_stack[self.state_sp].cur_entry_copy))
		# print ()


		if self.state_sp not in range (0, len (self.state_stack)):
			raise ()

		if len (self.state_stack) == 0:
			raise ()

		state = self.state_stack [self.state_sp]

		self.live_entryL = state.live_entryL_copy
		self.dead_entryS = state.dead_entryS_copy

		self._entry_pool [state.cur_entry_ind].rhn = state.cur_entry_copy.rhn

		self.cur_entry_ind = state.cur_entry_ind




	def handle_hit (self):

		self.save_state ()

		cur_entry = self._entry_pool [self.cur_entry_ind]
		cur_entry.rhn -= 1
		cur_entry.shots += 1
		cur_entry.hits += 1

		ll = len (self.live_entryL)


		if cur_entry.rhn > 0:

			if ll < 3:
				new_ind = ll
			else:
				if cur_entry.rhn == 1:
					new_ind = ll//2
				else:
					max_rhn = self.punitive_rhn

					x = max_rhn - cur_entry.rhn + 1
					new_ind = min (2**x, ll)

			self.live_entryL [new_ind:new_ind] = [self.cur_entry_ind]


		elif cur_entry.rhn == 0:

			print ("mydebug >>> Session.handle_hit cur_entry_ind {}".format (self.cur_entry_ind))
			print ("mydebug >>> Session.handle_hit live_entryL {}".format (self.live_entryL))

			self.dead_entryS.add (self.cur_entry_ind)

			if len (self.live_entryL) == 0:   # session ran out of entries
				print ("about to end the session")
				self.end ()
				return

		self.cur_entry_ind = self.live_entryL.pop (0)


	def handle_miss (self):

		self.save_state ()

		cur_entry = self._entry_pool [self.cur_entry_ind]

		cur_entry.shots += 1
		cur_entry.rhn = self.punitive_rhn

		if len (self.live_entryL) > 0:

			self.live_entryL [1:1] = [self.cur_entry_ind]
			self.cur_entry_ind = self.live_entryL.pop (0)


	class statistics ():
		def __init__ (self, shots, hits, kills, clean_kills, alive, untouched):
			self.shots = shots
			self.hits = hits
			self.kills = kills
			self.clean_kills = clean_kills
			self.alive = alive
			self.untouched = untouched


	def end (self):
		clean_kills_cnt = 0
		shots = 0
		hits = 0
		for ind in self.dead_entryS:
			e = self._entry_pool [ind]
			if e.shots == e.hits:
				clean_kills_cnt += 1
			shots += e.shots
			hits += e.hits

		untouched = 0
		for ind in self.live_entryL:
			e = self._entry_pool [ind]
			hits += e.hits
			shots += e.shots
			if e.shots == 0:
				untouched += 1

		self.stats = session.statistics (
								shots, hits, len (self.dead_entryS), clean_kills_cnt
								, len(self.live_entryL), untouched
								)
		self.running = False

	def is_alive (self):
		return len (self.live_entryL) > 0

	def get_cur_entry_ID (self):
		return self._entry_pool [self.cur_entry_ind].ID

	def get_cur_entry_rhn (self):
		return self._entry_pool [self.cur_entry_ind].rhn



"""
class engine ():
	def __init__ (self):
		self.running = False

	def stop (self):

		self.running = False


	def start (self):
		self.running = True

	def to_json (self):
		return {"running" : self.running}

	def from_json (self, json_obj):
		self.running = json_obj ['running']
"""
