import argparse
import logging


def get_command_arg_parser():
    _parser = argparse.ArgumentParser(description="Automatic Python environment configurator.")
    
    _parser.add_argument("--env_dir", dest="envDir", 
        required=True, help="Directory where Python environment will be stored.")
    _parser.add_argument("--exec", dest="rawCommands",
            nargs='+', help="Command(s) to be executed within given environment.", default=[])
    _parser.add_argument("--install", dest="install",
        nargs='+', help="List of packages to be installed", required=False)
    _parser.add_argument("--insall_from_file",
        help="File containing list of packages to be installed.")

    return _parser

if __name__ == "__main__":

    import os.path as p
    import sys
    _thisPkgDir = p.abspath(p.dirname(p.dirname(__file__)))
    if _thisPkgDir not in sys.path:
        sys.path.insert(0, _thisPkgDir)

    # from .
    from AutoEnv import environment


    logging.basicConfig()
    _logger = logging.getLogger()
    _logger.setLevel(logging.DEBUG)

    _parser = get_command_arg_parser()
    _args = _parser.parse_args()

    _env = environment.Environment(_args.envDir)
    _env.activate()

    if _args.insall_from_file:
        _env.installFromReqFile(_args.insall_from_file)

    if _args.install:
        _env.install(*_args.install)


    for _cmd in _args.rawCommands:
        exec(_cmd)

# vim: set sts=4 sw=4 et :
