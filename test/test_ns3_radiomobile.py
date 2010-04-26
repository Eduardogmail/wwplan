#!/usr/bin/python
# -*- coding: utf-8 -*
import unittest
import os
from StringIO import StringIO

import ns3
import lib
import radiomobile
import ns3_radiomobile as nr

class Ns3RadioMobileTest(unittest.TestCase):
    def _get_report_file(self):
        filename = "josjo.report.txt"
        return os.path.join(os.path.dirname(__file__), filename)

    def test_bracket_split(self):
        bs = nr.bracket_split
        self.assertEqual(bs("name1[name2]"), ("name1", "name2"))
        self.assertEqual(bs("name1  [name2]"), ("name1", "name2"))
        self.assertEqual(bs("name1"), ("name1", None))
        self.assertEqual(bs("[name2]"), ("", "name2"))
        
    def test_get_max_distance_in_network(self):
        node1 = lib.Struct("node1_mock", location=(10, 20)) 
        node2 = lib.Struct("node2_mock", location=(13, 24))
        node3 = lib.Struct("node3_mock", location=(12, 24))
        nodes = {"node1": node1, "node2": node2, "node3": node3}
        max_distance = nr.get_max_distance_in_network(nodes, "node1", ["node2", "node3"])
        self.assertEqual(max_distance, 5.0)

    def testget_netinfo_from_report(self):
        path = self._get_report_file()
        report = radiomobile.parse_report(path)
        netinfo = nr.get_netinfo_from_report(report)
        self.assert_(netinfo["units"])
        self.assert_(netinfo["networks"])
        self.assertEqual(sorted(netinfo["units"].keys()), 
            ['Ccatcca', 'Huiracochan', 'Josjojauarina 1', 'Josjojauarina 2', 'Kcauri', 'Urcos', 'Urpay'])
        urcos = netinfo["units"]["Urcos"]
        self.assertEqual(urcos["elevation"], 274)
        self.assertEqual(urcos["location"], [2533, -19694])

        self.assertEqual(sorted(netinfo["networks"].keys()), 
            ['Huiracochan', 'Josjo1', 'Josjo1-Josjo2', 'Josjo2'])

        josjo1 = netinfo["networks"]["Josjo1"]
        self.assertEqual(josjo1["mode"], {'standard': 'wifi', 'wifi_mode': 'wifia-6mbs'})
        self.assertEqual(josjo1["node"], {'name': 'Josjojauarina 1', 'system': 'wifi1'})
        self.assertEqual(josjo1["terminals"][0], 
            {'name': 'Urpay', 'system': 'wifi1'})
        self.assertEqual(josjo1["terminals"][1], 
            {'name': 'Huiracochan', 'system': 'wifi1'})
        
        josjo2 = netinfo["networks"]["Josjo2"]
        self.assertEqual(josjo2["mode"], {'standard': 'wimax', 'wimax_scheduler': 'rtps'})
        self.assertEqual(josjo2["node"], {'name': 'Josjojauarina 2', 'system': 'wimax1'})
        self.assertEqual(josjo2["terminals"][0], 
            {'name': 'Ccatcca', 'system': 'wimax2', 'wimax_mode': 'QAM64_34'})
        self.assertEqual(josjo2["terminals"][1], 
            {'name': 'Kcauri', 'system': 'wimax2', 'wimax_mode': 'QAM64_34'})

    def test_create_network_from_report_file(self):
        path = self._get_report_file()
        network = nr.create_network_from_report_file(path)
        josjo2 = network.nodes["Josjojauarina 2"]
        self.assertEqual(josjo2.name, "Josjojauarina 2")
        self.assert_(isinstance(josjo2.ns3_node, ns3.Node))         
        self.assertEqual(josjo2.location, [21728, 5837])
        
        self.assertEqual(josjo2.devices.keys(), ["wifi2", "wimax1"])
        wifi2 = josjo2.devices["wifi2"]
        self.assert_(isinstance(wifi2.ns3_device, ns3.WifiNetDevice))
        self.assert_(isinstance(wifi2.helper, ns3.WifiHelper))
        self.assert_(isinstance(wifi2.phy_helper, ns3.WifiPhyHelper))
        self.assertEqual(len(wifi2.interfaces), 1)
        self.assert_(isinstance(wifi2.interfaces[0].address, ns3.Ipv4Address))

        wimax1 = josjo2.devices["wimax1"]
        self.assert_(isinstance(wimax1.ns3_device, ns3.BaseStationNetDevice))
        self.assert_(isinstance(wimax1.helper, ns3.WimaxHelper))
        self.assertEqual(len(wimax1.interfaces), 1)
        self.assert_(isinstance(wimax1.interfaces[0].address, ns3.Ipv4Address))

    def test_main(self):
        path = self._get_report_file()
        stream = StringIO()
        retcode = nr.main([path], stream=stream)
        self.assertEqual(retcode, None)
        yml = stream.getvalue()        
        # just some basic tests
        self.assert_("networks:" in yml)
        self.assert_("units:" in yml)
        self.assert_("Urcos:" in yml)
                      
if __name__ == '__main__':
    unittest.main()
