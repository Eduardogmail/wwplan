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

def capture_stderr(func, *args, **kwargs):
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

class Ns3RadioMobileTest(unittest.TestCase):
    def _get_report_file(self):
        filename = "josjo.netinfo.yml"
        return os.path.join(os.path.dirname(__file__), filename)

    def test_simulation(self):    
        def simulation(network):
            ns3_lib.udp_echo_app(network, client_node="Urcos", server_node="Ccatcca", 
                server_device="Josjo2-wimax2", start=1.0, stop=9.0, packets=2, interval=1.0)
            ns3_lib.add_wimax_service_flow(network, install=("Ccatcca", "Josjo2-wimax2"), 
                source=("Urcos", "Huiracochan-wifi1", None), dest=("Ccatcca", "Josjo2-wimax2", 9), 
                protocol="udp", direction="down", scheduling="rtps", priority=0)
                
            monitor_info = ns3_lib.enable_monitor(network, interval=0.1)
            
            ns3.LogComponentEnable("UdpEchoClientApplication", ns3.LOG_LEVEL_INFO)
            ns3.LogComponentEnable("UdpEchoServerApplication", ns3.LOG_LEVEL_INFO)
            ns3_lib.run_simulation(network, 5.0)
            
            return monitor_info
            
        expected_debug = """
Sent 1024 bytes to 10.1.3.1
Received 1024 bytes from 10.1.0.1
Received 1024 bytes from 10.1.3.1
Sent 1024 bytes to 10.1.3.1
Received 1024 bytes from 10.1.0.1
Received 1024 bytes from 10.1.3.1""".strip()
        path = self._get_report_file()
        debug_data, monitor_info = capture_stderr(ns3_lib.simulation_main, 
            [path], simulation, "UDP server/client")
        self.assertEqual(debug_data.strip(), expected_debug)
        
        # Check monitor_info
        self.assertEqual(monitor_info["flow_stats_steps"].keys(), [1, 2])
        steps = monitor_info["flow_stats_steps"][1]
        time1, flow_stats1 = steps[0]
        time2, flow_stats2 = steps[1]
        self.assert_((time2-time1) - 0.1 < 0.01)
        self.assertEqual(len(steps), int((5.0 - 1.0) / 0.1) - 1)
        
        # Check print_monitor
        
        stream = StringIO()
        ns3_lib.print_monitor_results(monitor_info, show_histograms=True, stream=stream)
        results = stream.getvalue()        
         
        re_flow1 = r"^Flow 1 \(UDP\) - 10.1.0.1/\d+ \(Urcos:Huiracochan-wifi1\) --> 10.1.3.1/9 \(Ccatcca:Josjo2-wimax2\)"
        re_flow2 = r"^Flow 2 \(UDP\) - 10.1.3.1/9 \(Ccatcca:Josjo2-wimax2\) --> 10.1.0.1/\d+ \(Urcos:Huiracochan-wifi1\)"
        self.assert_(re.search(re_flow1, results, re.M))
        self.assert_(re.search(re_flow2, results, re.M))       
        
                     
if __name__ == '__main__':
    unittest.main()
