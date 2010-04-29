#!/usr/bin/python
# -*- coding: utf-8 -*
import unittest
import os
from StringIO import StringIO

from wwplan import radiomobile
from wwplan import netinfo

class Ns3RadioMobileTest(unittest.TestCase):
    def _get_report_file(self):
        filename = "josjo.report.txt"
        return os.path.join(os.path.dirname(__file__), filename)

    def test_bracket_split(self):
        bs = netinfo.bracket_split
        self.assertEqual(bs("name1[name2]"), ("name1", "name2"))
        self.assertEqual(bs("name1  [name2]"), ("name1", "name2"))
        self.assertEqual(bs("name1"), ("name1", None))
        self.assertEqual(bs("[name2]"), ("", "name2"))

    def test_get_netinfo_from_report(self):
        path = self._get_report_file()
        report = radiomobile.parse_report(path)
        info = netinfo.get_netinfo_from_report(report)
        self.assert_(info["units"])
        self.assert_(info["networks"])
        self.assertEqual(sorted(info["units"].keys()), 
            ['Ccatcca', 'Huiracochan', 'Josjojauarina 1', 
             'Josjojauarina 2', 'Kcauri', 'Urcos', 'Urpay'])
        urcos = info["units"]["Urcos"]
        self.assertEqual(urcos["elevation"], 274)
        self.assertEqual(urcos["location"], [2533, -19694])

        self.assertEqual(sorted(info["networks"].keys()), 
            ['Huiracochan', 'Josjo1', 'Josjo1-Josjo2', 'Josjo2'])

        josjo1 = info["networks"]["Josjo1"]
        self.assertEqual(josjo1["mode"], {'standard': 'wifi', 'wifi_mode': 'wifia-6mbs'})
        self.assertEqual(josjo1["node"], {'name': 'Josjojauarina 1', 'system': 'wifi1'})
        self.assertEqual(josjo1["terminals"][0], 
            {'name': 'Urpay', 'system': 'wifi1'})
        self.assertEqual(josjo1["terminals"][1], 
            {'name': 'Huiracochan', 'system': 'wifi1'})
        
        josjo2 = info["networks"]["Josjo2"]
        self.assertEqual(josjo2["mode"], {'standard': 'wimax', 'wimax_scheduler': 'rtps'})
        self.assertEqual(josjo2["node"], {'name': 'Josjojauarina 2', 'system': 'wimax1', 'wimax_mode': 'all'})
        self.assertEqual(josjo2["terminals"][0], 
            {'name': 'Ccatcca', 'system': 'wimax2', 'wimax_mode': 'QAM64_34'})
        self.assertEqual(josjo2["terminals"][1], 
            {'name': 'Kcauri', 'system': 'wimax2', 'wimax_mode': 'QAM64_34'})

    def test_main(self):
        path = self._get_report_file()
        stream = StringIO()
        retcode = netinfo.main([path], stream=stream)
        self.assertEqual(retcode, None)
        yml = stream.getvalue()        
        # just some basic tests
        self.assert_("networks:" in yml)
        self.assert_("units:" in yml)
        self.assert_("Urcos:" in yml)
                      
if __name__ == '__main__':
    unittest.main()
