""" Code to allow AutoEnv environment to inject itself into the python import routines ."""

import sys
import imp

class Injector(object):

	env = _names = None

	def __init__(self, env):
		self.env = env
		self._names = []

	def activate(self):
		if self.active:
			return
		sys.meta_path.append(self)


	def addAutoInstallModule(self, name):
		"""Add virtual python module that uses target environment and installs any missing libraries."""
		self._names.append(name)

	def find_module(self, name, path):
		"""sys.meta_path callback."""
		if any(name.startswith(myLib) for myLib in self._names):
			return self
		else:
			return None

	def load_module(self, name):
		if name in sys.modules:
			return sys.modules[name]

		myLib = [pkgName for pkgName in self._names if name.startswith(pkgName)]
		assert len(myLib) == 1
		myLib = myLib[0]

		if myLib == name:
			# Top-level package
			mod = imp.new_module(name)
			mod.__file__ = "<Magically created by {}>".format(self.__class__.__name__)
			mod.__loader__ = self
			mod.__package__ = name
			mod.__path__ = []
		else:
			# Sub-package. 'name' in in format <myLib>.<pkgName>
			assert name.startswith(myLib + ".")
			actualImport = name[len(myLib)+1:]
			self.env.installIfMissing(actualImport)
			assert self.env.activated
			mod = __import__(actualImport)

		sys.modules[name] = mod
		return mod

	@property
	def active(self):
		signs = (
			self in sys.meta_path,
		)
		rv = all(signs)
		if rv != any(signs):
			raise RuntimeError("Consistency error: Something is wrong with system injector. State: {!r}".format(signs))
		return rv
