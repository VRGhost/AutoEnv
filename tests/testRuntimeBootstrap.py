
import unittest

import shutil

from . import unittestEnv

import AutoEnv

class TestRuntimeBootstrap(unittest.TestCase):
    """Test runtime environment modification."""

    def setUp(self):
        self.envDir = unittestEnv.mkTempDir()

    def tearDown(self):
        shutil.rmtree(self.envDir)

    def testBootstap(self):
        with self.assertRaises(ImportError):
            import bottle

        _boot = AutoEnv.Bootstrap(self.envDir, logging=True, requirements="bottle")

        import bottle
        self.assertTrue(bottle, "`bottle` module must be present now")

# vim: set sts=4 sw=4 et :
