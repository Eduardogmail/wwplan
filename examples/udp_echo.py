#!/usr/bin/python
import sys
import ns3
import ns3_lib

ns3.LogComponentEnable("UdpEchoClientApplication", ns3.LOG_LEVEL_INFO | ns3.LOG_PREFIX_TIME)
ns3.LogComponentEnable("UdpEchoServerApplication", ns3.LOG_LEVEL_INFO | ns3.LOG_PREFIX_TIME)

def simulation(network):
    # Applications
    ns3_lib.udp_echo_app(network, client_node="Urcos", server_node="Ccatcca", 
        server_device="Josjo2-wimax2", start=1.0, stop=9.0, packets=2, interval=1.0)
    ns3_lib.add_wimax_service_flow(network, install=("Ccatcca", "Josjo2-wimax2"), 
        source=("Urpay", "Josjo1-wifi1", None), dest=("Ccatcca", "Josjo2-wimax2", 9), 
        protocol="udp", direction="down", scheduling="rtps", priority=0)
    
    # Tracing
    #device = network.nodes["Josjojauarina 1"].devices["Josjo1-wifi1"]
    #device.phy_helper.EnablePcap("udp_echo", device.ns3_device)

    # Run simulation    
    ns3_lib.run_simulation(network, 10.0)
    
if __name__ == '__main__':
    sys.exit(ns3_lib.simulation_main(sys.argv[1:], simulation,
        "UDP server/client ping"))
