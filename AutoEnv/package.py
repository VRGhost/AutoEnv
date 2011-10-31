
class BasePackage(object):
    """Base package class"""

    name = None # Name of the package

    def __init__(self, name):
        self.name = name

    def _extraReprTail(self):
        return ""

    def __repr__(self):
        return "<{0} : {1!r} {2}>".format(self.__class__.__name__, self.name, self._extraReprTail())

class Package(BasePackage):
    """Package object created from the pip-supplied information."""

    def __init__(self, name, humanVersion, version):
        super(Package, self).__init__(name)
        self.version = version
        self.humanVersion = humanVersion

    @classmethod
    def fromPipDistribution(cls, pipDist):
        return cls(pipDist.key, pipDist.version, pipDist.parsed_version)

    def _extraReprTail(self):
        return "version={0}".format(self.humanVersion)

class RequiredPackage(BasePackage):
    """Package required for program to execute"""

    def __init__(self, name):
        super(RequiredPackage, self).__init__(name)

    def toCommandLineArguments(self):
        return [self.name]

    def satisfiedBy(self, other):
        # TODO: add version check
        assert (self.name == other.name) == (self.name.lower() == other.name.lower()), \
            "Using case-insensetive package name match is not allowed to change comparison result"
        return self.name == other.name

    @classmethod
    def construct(cls, initData):
        """Creates 'RequiredPackage' structure from an variety of input data formats."""
        if isinstance(initData, cls):
            # We are asked to construct our class from an instance of our class.
            # Skip the hassle and return the input object as result
            # (Shouldn't caouse any problems as objects of this class are expected to be immutable)
            _rv = initData
        elif isinstance(initData, basestring):
            # Expecting for `initData` to contain only the package name
            _rv = cls(initData)
        elif isinstance(initData, dict):
            _rv = cls(**initData)
        else:
            raise NotImplementedError("Don't know how to construct {0} from {1!r}".format(cls, initData))

        return _rv

# vim: set sts=4 sw=4 et :
