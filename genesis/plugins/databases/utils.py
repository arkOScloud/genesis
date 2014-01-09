class DBConnFail(Exception):
	def __init__(self, dbtype, op=None):
		self.dbtype = dbtype
		self.op = op

	def __str__(self):
		if op:
			return 'The database connection for %s failed, while performing %s' % (self.dbtype, self.op)
		else:
			return 'The database connection for %s failed generally' % self.dbtype


class DBAuthFail(Exception):
	def __init__(self, dbtype):
		self.dbtype = dbtype

	def __str__(self):
		return 'Authentication for %s failed, did you use the correct password?' % self.dbtype

