#!/usr/bin/python
# -*- coding: utf-8 -*
import unittest
import os
from StringIO import StringIO

import ns3
from wwplan import lib
from wwplan import radiomobile
from wwplan import network as wwnetwork

class Ns3RadioMobileTest(unittest.TestCase):
    def _get_report_file(self):
        filename = "josjo.report.txt"
        return os.path.join(os.path.dirname(__file__), filename)
        
    def test_get_max_distance_in_network(self):
        node1 = lib.Struct("node1_mock", location=(10, 20)) 
        node2 = lib.Struct("node2_mock", location=(13, 24))
        node3 = lib.Struct("node3_mock", location=(12, 24))
        nodes = {"node1": node1, "node2": node2, "node3": node3}
        max_distance = wwnetwork.get_max_distance_in_network(nodes, "node1", ["node2", "node3"])
        self.assertEqual(max_distance, 5.0)

    def test_create_network_from_report_file(self):
        path = self._get_report_file()
        network = wwnetwork.create_network_from_report_file(path)
        josjo2 = network.nodes["Josjojauarina 2"]
        self.assertEqual(josjo2.name, "Josjojauarina 2")
        self.assert_(isinstance(josjo2.ns3_node, ns3.Node))         
        self.assertEqual(josjo2.location, [21728, 5837])
        
        self.assertEqual(set(josjo2.devices.keys()), 
            set(["Josjo1-Josjo2-wifi2", "Josjo2-wimax1"]))
        wifi2 = josjo2.devices["Josjo1-Josjo2-wifi2"]
        self.assert_(isinstance(wifi2.ns3_device, ns3.WifiNetDevice))
        self.assert_(isinstance(wifi2.helper, ns3.WifiHelper))
        self.assert_(isinstance(wifi2.phy_helper, ns3.WifiPhyHelper))
        self.assertEqual(len(wifi2.interfaces), 1)
        self.assert_(isinstance(wifi2.interfaces[0].address, ns3.Ipv4Address))

        wimax1 = josjo2.devices["Josjo2-wimax1"]
        self.assert_(isinstance(wimax1.ns3_device, ns3.BaseStationNetDevice))
        self.assert_(isinstance(wimax1.helper, ns3.WimaxHelper))
        self.assertEqual(len(wimax1.interfaces), 1)
        self.assert_(isinstance(wimax1.interfaces[0].address, ns3.Ipv4Address))
                      
if __name__ == '__main__':
    unittest.main()
