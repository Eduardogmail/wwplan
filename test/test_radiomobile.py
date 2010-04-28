#!/usr/bin/python
# -*- coding: utf-8 -*
import os
import unittest
from datetime import datetime

from wwplan import radiomobile

class RadioMobileReportTest(unittest.TestCase):
    def setUp(self):
        filename = "josjo.report.txt"
        path = os.path.join(os.path.dirname(__file__), filename)
        self.report = radiomobile.parse_report(path)

    def test_get_position_from_reference(self):
        unit1 = (40.86, 0.16)
        unit2 = (41.38, 2.17)
        reference = radiomobile.get_reference(unit1)
        position1 = radiomobile.get_position_from_reference(unit1, reference)
        self.assertEqual(position1, (0.0, 0.0))
        position2 = radiomobile.get_position_from_reference(unit2, reference)
        self.assertEqual(position2, (169469, 57747))
              
    def test_generated_on(self):
        self.assertEqual(datetime(2010, 4, 14, 13, 56, 45), self.report.generated_on)
                      
    def test_units(self):
        units = self.report.units
        expected_units = ['Josjojauarina 1', 'Josjojauarina 2', 'Ccatcca', 'Kcauri', 'Urpay', 'Huiracochan', 'Urcos'] 
        self.assertEqual(expected_units, units.keys())
    
    def test_unit_details(self):
        units = self.report.units
        urpay = units["Urpay"]
        self.assertEqual("""09°19'45"S 075°17'41"W FI20IQ""", urpay.location) 
        self.assertEqual(248, urpay.elevation) 
            
    def test_systems(self):
        systems = self.report.systems
        expected_systems = ['wifi1', 'wifi2', 'wimax1', 'wimax2 [QAM64_34]', 'Sistema   5', 'Sistema   6', 'Sistema   7', 'Sistema   8', 'Sistema   9', 'Sistema  10', 'Sistema  11', 'Sistema  12', 'Sistema  13', 'Sistema  14', 'Sistema  15', 'Sistema  16', 'Sistema  17', 'Sistema  18', 'Sistema  19', 'Sistema  20', 'Sistema  21', 'Sistema  22', 'Sistema  23', 'Sistema  24', 'Sistema  25']
        self.assertEqual(expected_systems, systems.keys())

    def test_system_details(self):
        systems = self.report.systems
        w = systems["wifi1"]
        self.assertEqual("10,000W", w.pwr_tx)
        self.assertEqual("0,5dB", w.loss) 
        self.assertEqual("0,000dB/m", getattr(w, "loss_(+)"))
        self.assertEqual("-107,0dBm", w.rx_thr)
        self.assertEqual("2,0dBi", w.ant_g)
        self.assertEqual("omni.ant", w.ant_type)

    def test_nets(self):
        nets = self.report.nets
        expected_nets = ['Josjo1-Josjo2 [wifia-6mbs]', 'Josjo2 [wimax-rtps]', 'Josjo1 [wifia-6mbs]', 'Huiracochan [wifia-6mbs]']
        self.assertEqual(expected_nets, nets.keys())
        
        net1 = nets['Josjo1-Josjo2 [wifia-6mbs]']
        self.assertEqual(50, net1.max_quality)
        self.assertEqual(1, len(net1.links))

    def test_net_details(self):
        net1 = self.report.nets['Josjo1 [wifia-6mbs]']
        links = net1.links
        
        link1, link2 = links       
        self.assertEqual(16370, link1.distance)
        self.assertEqual(62, link1.quality)
        self.assertEqual(('Josjojauarina 1', 'Urpay'), link1.peers)        

        self.assertEqual(81, link2.quality)        
        self.assertEqual(('Josjojauarina 1', 'Huiracochan'), link2.peers)
        
        member1 = net1.net_members["Urpay"]
        self.assertEqual("Slave", member1.role)
        self.assertEqual("2,0m", member1.antenna) 

        member2 = net1.net_members["Huiracochan"]
        self.assertEqual("2,0m", member2.antenna) 
        self.assertEqual("Slave", member2.role)

    def test_get_units_for_network(self):
        net2 = self.report.nets.values()[1]
        self.assertEqual(['Josjojauarina 2'],
            list(radiomobile.get_units_for_network(net2, "Master")))
        self.assertEqual(['Ccatcca', 'Kcauri'],
            list(radiomobile.get_units_for_network(net2, "Slave")))
                
if __name__ == '__main__':
    unittest.main()
