import sys
import os
import urllib
import logging
import platform
import tempfile
import threading

from . import (
    cmd,
    package,
    subProc,
    inject,
)

class Environment(object):
    """Object that represents single Python environment."""
    
    root = activated = None

    _injector = None

    def __init__(self, dir, createDir=False):
        """`dir` is a directore where given environment is stored."""

        self.root = os.path.abspath(dir)
        self._injector = inject.Injector(self)

        if not os.path.exists(dir) and createDir:
                os.makedirs(dir)
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
            assert len(_args) > 2, "{0!r} hust add something to command line.".format(_pkg)
            _cmds.append(cmd.Command(_args))
        self._safeCall(cmd.SuccessSequence(_cmds))

    def installFromReqFile(self, reqFile):
        """Install requirements from requirements file."""
        if not os.path.isfile(reqFile):
            raise RuntimeError("Requirements file {0!r} does not exist.".format(reqFile))
        _command = cmd.Command(["pip", "install", "-r", reqFile])
        self._safeCall(_command)

    _strInstallLock = threading.Lock()

    def installFromReqStr(self, requirements):
        """Install requirements from provided string."""
        with self._strInstallLock:
            (_fHandle, _fileName) = tempfile.mkstemp(dir=self.root, text=True)
            os.write(_fHandle, requirements)
            os.close(_fHandle)

            try:
                self.installFromReqFile(_fileName)
            except:
                logging.error("Failed to install requirements from string {0!r}".format(requirements))
            finally:
                os.unlink(_fileName)

    
    def installIfMissing(self, *pkgs):
        _pkgs = [package.RequiredPackage.construct(_el) for _el in pkgs]
        _installed = self.getPkgInfo(_pkgs)
        _toBeInstalled = []
        for _req in _pkgs:
            if not any(_req.satisfiedBy(_el) for _el in _installed):
                _toBeInstalled.append(_req)

        if _toBeInstalled:
            self.install(*_toBeInstalled)

        return _toBeInstalled

    def injectAutoInstallModule(self, name):
        """Inject into Python import hooks to attempt installing modules on import."""
        self._activated()
        self._injector.activate()
        return self._injector.addAutoInstallModule(name)
    
    def _safeCall(self, cmd):
        _rc = self.call(cmd)
        if _rc != 0:
            raise RuntimeError("Install command {0!r} failed with rc {1}".format(cmd, _rc))
        
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
        return subProc.Popen(_cmd, **kwargs)

    def getInstalledPackages(self):
        self._activated()

        from pip import util
        return [
            package.Package.fromPipDistribution(_pkg)
            for _pkg in util.get_installed_distributions()
        ]

    def getPkgInfo(self, packages):
        _pkgs = [package.RequiredPackage.construct(_el) for _el in packages]
        _out = []
        for _el in self.getInstalledPackages():
            if any(_pkg.satisfiedBy(_el) for _pkg in _pkgs):
                _out.append(_el)
        return _out

    def getSinglePkgInfo(self, pkgs):
        _info = self.getPkgInfo((pkgs, ))
        assert len(_info) <= 1
        if _info:
            _rv = _info[0]
        else:
            _rv = None
        return _rv

    def _activated(self):
        """Ensure that current environment is activated."""

        if not self.activated:
            logging.warning("Environment was not activated while executing command requires for it to be.")
            logging.warning("Forcing environment activation.")
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
            if _reqDir.lower() not in _contents:
                return False
        return True


    def __repr__(self):
        return "<{0} dir={1!r}>".format(self.__class__.__name__, self.root)

# vim: set sts=4 sw=4 et :
