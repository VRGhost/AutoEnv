import sys
import os
import urllib
import logging
import platform

from . import (
    cmd,
    package,
    subProc,
)

class Environment(object):
    """Object that represents single Python environment."""
    
    root = activated = None

    def __init__(self, dir):
        """`dir` is a directore where given environment is stored."""

        self.root = os.path.abspath(dir)
        if not os.path.isdir(dir):
            raise RuntimeError("Root environment directory {0!r} does not exist.".format(self.root))
        
        if not self._isEnvInitialised():
            # Assuming new directory with no virtualenv installed.
            self._bootstrap()

    def activate(self):
        _pyActivate = self._envPath(self._binDirectory, "activate_this.py")
        execfile(_pyActivate, {"__file__": _pyActivate})
        self.activated = True

    def install(self, *pkgs):
        _cmds = []
        for _el in pkgs:
            _pkg = package.RequiredPackage.construct(_el)
            _args = ["pip", "install"]
            _args.extend(_pkg.toCommandLineArguments())
            _cmds.append(cmd.Command(_args))

        _rc = self.call(cmd.SuccessSequence(_cmds))
        if _rc != 0:
            raise RuntimeError("Installing package {0!r} failed with rc {1}".format(_el, _rc))
    
    def installIfMissing(self, *pkgs):
        _installed = [_el["name"] for _el in self.getInstalledPackages()]
        self.install(*(_name for _name in pkgs if _name not in _installed))
        
    def call(self, cmd, **kwargs):
        return self.popen(cmd, **kwargs).wait()

    def popen(self, shellCmd, **kwargs):
        _activateScript = self._envPath(self._binDirectory, "activate")
        _activateInject = cmd.shell_inject_env_command()

        _activateCmd = []
        if _activateInject:
            _activateCmd.append(_activateInject)
        _activateCmd.append(_activateScript)

        _execCommand = cmd.SuccessSequence((
            cmd.Command(_activateCmd),
            cmd.Command(shellCmd),
        ))
        _cmd = []
        _cmd.extend(cmd.shell_exec_cmdline())
        _cmd.append(_execCommand.toCmdline())
        print _cmd
        return subProc.Popen(_cmd, **kwargs)

    def getInstalledPackages(self):
        self._activated()

        from pip import util
        return [
            package.Package.fromPipDistribution(_pkg)
            for _pkg in util.get_installed_distributions()
        ]

    def getPkgInfo(self, pkg):
        _pkg = package.RequiredPackage.construct(pkg)
        _installed = [_el for _el in self.getInstalledPackages() if _pkg.satisfiedBy(_el)]
        assert len(_installed) <= 1
        if _installed:
            _rv = _installed[0]
        else:
            _rv = None
        return _rv

    def _activated(self):
        """Ensure that current environment is activated."""

        if not self.activated:
            self.activate()

    def _bootstrap(self):
        """Ensure minimal configuration environment configuration."""
        
        logging.info("No environment detected, performing bootstrap.")

        _virtualenv = self._envPath("virtualenv.py")
        if not os.path.exists(_virtualenv):
            with open(_virtualenv, "wb") as _f:
                _f.write(self._urlget(r"https://raw.github.com/pypa/virtualenv/master/virtualenv.py"))
        
        assert os.path.exists(_virtualenv)
        # setup virtualenv
        _rc = subProc.call(
            [sys.executable, _virtualenv, os.path.basename(self.root)],
            cwd=os.path.dirname(self.root),
        )
        if _rc != 0:
            raise RuntimeError("Virtualenv setup failed.")
        else:
            os.unlink(_virtualenv)
            if "virtualenv.pyc" in os.listdir(self.root):
                os.unlink(self._envPath("virtualenv.pyc"))

    def _urlget(self, url):
        return urllib.urlopen(url).read()

    def _envPath(self, *args):
        return os.path.join(self.root, *args)

    _binDirectoryCache = None
    @property
    def _binDirectory(self):
        if not self._binDirectoryCache:
            if platform.system() == "Windows":
                _dir = "Scripts"
            else:
                _dir = "bin"
            self._binDirectoryCache = self._envPath(_dir)
        return self._binDirectoryCache

    def _isEnvInitialised(self):
        _contents = [_el.lower() for _el in os.listdir(self.root)]
        for _reqDir in ("lib", "include", os.path.basename(self._binDirectory)):
            if _reqDir not in _contents:
                return False
        return True


    def __repr__(self):
        return "<{0} dir={1!r}>".format(self.__class__.__name__, self.root)

# vim: set sts=4 sw=4 et :
