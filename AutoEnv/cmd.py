import itertools
import collections

from subprocess import list2cmdline

class _Cmd(object):
    """Command line prototype."""

    args = None


    def toCmdline(self):
        raise NotImplementedError

    def __repr__(self):
        return "<{0} {1}>".format(self.__class__.__name__, self.args)

class _StringCommand(_Cmd):
    """Low-level string-based command."""

    def __init__(self, args):
        self.args = tuple(args)

    def toCmdline(self):
        return list2cmdline(self.args)

class Command(_Cmd):
    """Command to be executed in current system's command line."""
    
    def __init__(self, args):
        _args = []

        if not isinstance(args, collections.Iterable):
            args = (args, )

        for (_key, _group) in itertools.groupby(args, lambda el: hasattr(el, "toCmdline")):
            if _key:
                # High-level objects
                _args.extend(_group)
            else:
                # Low-level object
                _args.append(_StringCommand(_group))
        self.args = tuple(_args)

    def toCmdline(self):
        return " ".join(_el.toCmdline() for _el in self.args)

class SuccessSequence(Command):
    """Command sequence that executes each successive part only if previous command suceeded executing."""

    def toCmdline(self):
        return " && ".join(_el.toCmdline() for _el in self.args)

# vim: set sts=4 sw=4 et :
