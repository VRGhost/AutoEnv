import argparse

# from .
import environment

def get_command_arg_parser():
    _parser = argparse.ArgumentParser(description="Automatic Python environment configurator.")
    
    _parser.add_argument("--env_dir", dest="envDir", help="Directory where Python environment will be stored.")
    _parser.add_argument(
        "--exec", dest="rawCommands", nargs='+', help="Command(s) to be executed within given environment.")
    _parser.add_argument(
        "--install", dest="install", nargs='+', help="List of packages to be installed", required=False)

    return _parser

if __name__ == "__main__":
    _parser = get_command_arg_parser()
    _args = _parser.parse_args()

    _env = environment.Environment(_args.envDir)
    _env.activate()

    if _args.install:
        _env.installPackages(_args.install)

    for _cmd in _args.rawCommands:
        exec(_cmd)

# vim: set sts=4 sw=4 et :
