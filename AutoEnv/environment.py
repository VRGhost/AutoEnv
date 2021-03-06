import imp
import logging
import os
import platform
import sys
import tempfile
import threading
import urllib

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

    def __init__(self, dir, createDir=False, relocatable=True, dynamicInstall=True):
        """`dir` is a directore where given environment is stored."""

        self.root = os.path.abspath(dir)
        self._injector = inject.Injector(self)
        self._relocatable = relocatable
        self.doInstalls = dynamicInstall

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

    def install(self, *pkgs, **kwargs):
        if not self.doInstalls:
            raise RuntimeError("Dynamic package installation disabled.")
        if not pkgs:
            return
        _cmds = []
        for _el in pkgs:
            _pkg = package.RequiredPackage.construct(_el)
            _args = ["pip", "install"]
            if kwargs.get("ignoreSystemPackages"):
                _args.append("--ignore-installed")
            _args.extend(_pkg.toCommandLineArguments())
            assert len(_args) > 2, "{0!r} hust add something to command line.".format(_pkg)
            _cmds.append(cmd.Command(_args))
        self._safeCall(cmd.SuccessSequence(_cmds))

    def installFromReqFile(self, reqFile, **kwargs):
        """Install requirements from requirements file."""
        if not self.doInstalls:
            raise RuntimeError("Dynamic package installation disabled.")

        if not os.path.isfile(reqFile):
            raise RuntimeError("Requirements file {0!r} does not exist.".format(reqFile))

        _cmd = ["pip", "install", ]
        if kwargs.get("ignoreSystemPackages"):
            _cmd.append("--ignore-installed")
        _cmd.extend(["-r", reqFile])
        _command = cmd.Command(_cmd)
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
            except Exception as err:
                logging.error("Failed to install requirements from string {!r}: {}".format(requirements, err))
            finally:
                os.unlink(_fileName)

    
    def installIfMissing(self, *pkgs, **kwargs):
        _pkgs = [package.RequiredPackage.construct(_el) for _el in pkgs]
        
        _toInstall = []
        for _req in _pkgs:
            try:
                imp.find_module(_req.name)
            except ImportError:
                _toInstall.append(_req)

        if _toInstall:
            self.install(*_toInstall, **kwargs)

        return _toInstall

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
        _rc = subProc.call([sys.executable, _virtualenv, os.path.basename(self.root)], cwd=os.path.dirname(self.root))
        if _rc != 0:
            raise RuntimeError("Virtualenv setup failed.")

        if self._relocatable:
            _rc = subProc.call([sys.executable, _virtualenv, "--relocatable", os.path.basename(self.root)], cwd=os.path.dirname(self.root))
            if _rc != 0:
                raise RuntimeError("Virtualenv setup failed.")

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
        for _reqDir in ("lib", os.path.basename(self._binDirectory)):
            if _reqDir.lower() not in _contents:
                return False
        return True


    def __repr__(self):
        return "<{0} dir={1!r}>".format(self.__class__.__name__, self.root)

# vim: set sts=4 sw=4 et :
