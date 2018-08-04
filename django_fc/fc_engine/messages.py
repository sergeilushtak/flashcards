

class Msg ():
	def __init__ (self, whose, what, data):
		self.whose = whose
		self.what = what
		self.data = data

__message_q__ = []

def send (to_whom, what, data):
	global __message_q__

	__message_q__ .append (Msg (to_whom, what, data))

def get_all_my_messages (whose, what):

	global __message_q__

	ind = 0
	ret = []
	while ind < len (__message_q__):
		msg = __message_q__ [ind]
		if msg.whose == whose and msg.what == what: 
			ret.append (msg)
			__message_q__.pop (ind)
		else:
			ind += 1

	return ret
