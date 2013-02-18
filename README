If you are active Python developer who manages a lot of various weakly related applications with
wide set of functionality, most of which is provided by 3rd party libraries, than you might find this library as beneficial as it is for me.

Over the years of freelance development and hobby programming, I have discovered myself setting up numerous virtualenvs, each requireing me to
download/install `virtualenv` package, invoke with list of libraries required (generated ether from my head, or point it to the special config file.
Meaning that there is one more config to manage.).

As any sane software developer, I have intristic urge to script any piece of work that I had to perform more than thee times.

This is how =AutoEnv= project was born.

Designed to be included in ones' parent project as git submodule, it empowers any software developer to drive his coworkers crazy faster than a shot of Pan Galactic Gargle Blaster!

Basically, what it does is automatic download, setup and injection of `virtualenv` in to your project. And this is in the runtime of your project.

This project has no external dependencies but presence of working Internet connection (and Internet communication can be actually disabled later,
if you are certain that you won't need to install any more packages).

Only thing that you, developer, are required to do -- is to invoke single `AutoEnv.hotshot` function. With no mandatory arguments. It returns `Environment` object that can be used later for obscure stuff.

Declaration of `hosthot` function is as follows:
```python
def hotshot(rootDir=None, envDirName="_env", relocatable=True, dynamicInstall=True)
```

By default, the `hotshot` function creates virtualenv in a new directory called `_env` located in a same directory where `AutoEnv` resides.
To change that behavior, you have to set values for `rootDir` and `envDirName` arguments.

The `relocatable` argument controls if newly created virtualenv will be relocatable or not (decision is made once in the initial setup phase). Relocatable environments are
useful as you get ability to move your project (and, incidentally, its environment) in the directory tree and even transfer it between computers (with certain limitations: target computer has to have same CPU architecture, same Python version and same OS flavor). I am using this feature to wrap up my project with all its dependencies to CentOS RPM packages.

The `dynamicInstall` argument controls AutoEnvs' ability to install packages on the fly. Meaning that within single run of you application, you may decide that you need certain package, request it and `AutoEnv` will download, install and enable it to be importable for the calling process.

Most useful (and hotshot-y) way of requesting package to be installed and imported is via registration of import hook. 
E.g.:
```python

environment = AutoEnv.hotshot()
environment.injectAutoInstallModule("wonderland")

```

And, from now on, any `from wonderland import <pkg>` (or `import wonderland.<pkg>`) will ether import given package with optional invocation of 
`pip install <pkg>` (from within controlled `virtualenv`).
So, if you are doing `from wonderland import markdown` call and `markdown` is not installed, it will be automatically downloaded, installed and than stressfully imported to you projects' namespace. It won't even notice that this library wasn't there.

[TBC]