#!/usr/bin/python
import unittest
import os
import sys
import tempfile
import re
from StringIO import StringIO

import ns3
from wwplan import radiomobile
from wwplan import ns3_lib
from wwplan import run_siminfo

def capture_output(func, *args, **kwargs):
    fd = tempfile.TemporaryFile()
    old_stderr = os.dup(sys.stderr.fileno())
    os.dup2(fd.fileno(), sys.stderr.fileno())
    try:
        retvalue = func(*args, **kwargs)
    except Exception:
        os.dup2(old_stderr, sys.stderr.fileno())
        raise        
    fd.seek(0)
    error_data = fd.read()
    fd.close()
    os.dup2(old_stderr, sys.stderr.fileno())
    return error_data, retvalue

class RunSiminfoTest(unittest.TestCase):
    def _get_netinfo_file(self):
        filename = "udp_echo.siminfo.yml"
        return os.path.join(os.path.dirname(__file__), filename)

    def test_siminfo(self):
        netinfo_path = self._get_netinfo_file()
        stream = StringIO()
        err, retval = capture_output(run_siminfo.siminfo, netinfo_path, stream=stream)
        expected_debug = """
Sent 1024 bytes to 10.1.3.1
Received 1024 bytes from 10.1.0.1
Received 1024 bytes from 10.1.3.1
Sent 1024 bytes to 10.1.3.1
Received 1024 bytes from 10.1.0.1
Received 1024 bytes from 10.1.3.1""".strip().splitlines()
        # remove first field (time)
        err2 = [" ".join(s.split()[1:]) for s in err.splitlines()]
        self.assertEqual(err2, expected_debug)
        results = stream.getvalue()
        re_flow1 = r"^Flow 1 \(UDP\) - 10.1.0.1/\d+ \(Urcos:Huiracochan-wifi1\) --> 10.1.3.1/9 \(Ccatcca:Josjo2-wimax2\)"
        re_flow2 = r"^Flow 2 \(UDP\) - 10.1.3.1/9 \(Ccatcca:Josjo2-wimax2\) --> 10.1.0.1/\d+ \(Urcos:Huiracochan-wifi1\)"
        self.assert_(re.search(re_flow1, results, re.M))
        self.assert_(re.search(re_flow2, results, re.M))       
        
                     
if __name__ == '__main__':
    unittest.main()
