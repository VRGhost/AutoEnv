
import unittest

import shutil

from . import unittestEnv

try:
    from .. import AutoEnv
except (ImportError, ValueError):
    import AutoEnv

class TestBasicEnvGeneration(unittest.TestCase):
    """Test runtime environment modification."""

    def setUp(self):
        self.envDir = unittestEnv.mkTempDir()
        self.env = AutoEnv.Environment(self.envDir)
        self.env.activate()

    def tearDown(self):
        shutil.rmtree(self.envDir)

    def testInstall(self):
        with self.assertRaises(ImportError):
            import wget

        self.env.installIfMissing("wget")
        import wget
        self.assertTrue(wget, "Wget module must be present now")

    def testInstallIfMissing(self):
        with self.assertRaises(ImportError):
            import bottle

        # Test that successive calls do not have any effect
        self.assertTrue(self.env.installIfMissing("bottle"))
        for _x in xrange(10):
            self.assertFalse(self.env.installIfMissing("bottle"))

        import bottle
        self.assertTrue(bottle, "Bottle module must be present now")

    def testCustomImportHook(self):
        self.env.injectAutoInstallModule("magicAutoInstallModule")
        from magicAutoInstallModule import markdown
        self.assertTrue(markdown, "Markdown is expected to be downloaded and imported.")


# vim: set sts=4 sw=4 et :
