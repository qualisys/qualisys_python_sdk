import json
import sys

from twisted.trial import unittest
from twisted.python.failure import Failure
import twisted

from qtm import QRest
from qtm.util import RestError


class TestUnreachable(unittest.TestCase):
    def setUp(self):
        self.rest = QRest("192.0.2.0", 7979)
        self.rest.persistent = False

    def tearDown(self):
        self.rest = None

    def test_not_reachable(self):
        d = self.rest.get_settings()
        d.addErrback(self.validate_failure, -1)
        return d

    def validate_failure(self, failure, code):
        self.assertIsInstance(failure, Failure)
        self.assertIsInstance(failure.value, RestError)
        self.assertEqual(failure.value.code, code)


class TestSettings(unittest.TestCase):
    def setUp(self):
        self.rest = QRest("127.0.0.1", 7979)
        self.rest.persistent = False

    def tearDown(self):
        self.rest = None

    def test_get_settings(self):
        d = self.rest.get_settings()
        d.addCallback(self.assertIsInstance, dict)
        return d

    def test_set_settings_empty(self):
        d = self.rest.set_settings()
        d.addErrback(self.validate_failure, 400)
        return d

    def test_set_settings_c3d(self):
        c3d_settings = '''{"ExportC3d": {
                         "ExcludeEmpty": false,
                         "ExcludeNonFullFrames": true,
                         "ExcludeUnidentified": true,
                         "FileName": "",
                         "FullLabels": false,
                         "UseCroppedStartTimeForEvents": false,
                         "UseZeroBaseline": true,
                         "ZeroBaselineStart": 0,
                         "ZeroBaselineStop": 10
                     }}'''
        data = json.loads(c3d_settings)

        d = self.rest.set_settings(data=data)
        d.addCallback(self.validate_dict, "ExportC3d")
        return d

    def test_get_root(self):
        d = self.rest.get_root()
        d.addCallback(self.assertEqual, ['api'])
        return d

    def test_get_api(self):
        d = self.rest.get_api()
        d.addCallback(self.assertEqual, ['v1'])
        return d

    def test_get_v1(self):
        d = self.rest.get_v1()
        d.addCallback(self.assertEqual, ['paf', 'project', 'version'])
        return d

    def test_get_experimental(self):
        d = self.rest.get_experimental()
        d.addCallback(self.assertEqual, ['command', 'measurements', 'settings', 'workerstate'])
        return d

    def test_get_workerstate(self):
        d = self.rest.get_workerstate()

        if sys.version_info > (3, 0):
            d.addCallback(self.assertIsInstance, str)
        else:
            d.addCallback(self.assertIsInstance, unicode)
        return d

    def test_get_cameras(self):
        d = self.rest.get_cameras()
        d.addCallback(self.validate_dict, 'Cameras')
        return d

    def test_get_all_cameras(self):
        d = self.rest.get_all_cameras()
        d.addCallback(self.validate_dict, 'AllCameras')
        return d

    def validate_dict(self, result, validation):
        self.assertIsInstance(result, dict)
        self.assertIn(validation, result)

    def validate_failure(self, failure, code):
        self.assertIsInstance(failure, Failure)
        self.assertIsInstance(failure.value, RestError)
        self.assertEqual(failure.value.code, code)


if __name__ == '__main__':
    unittest.main()
