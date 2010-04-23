#!/usr/bin/python
import sys
import ns3
import ns3_lib

ns3.LogComponentEnable("UdpEchoClientApplication", ns3.LOG_LEVEL_INFO)
ns3.LogComponentEnable("UdpEchoServerApplication", ns3.LOG_LEVEL_INFO)

def simulation(network):
    # Applications
    ns3_lib.udp_echo_app(network, client_node="Urcos", server_node="Ccatcca", 
        server_device="wimax2", start=1.0, stop=9.0, packets=2, interval=1.0)
    ns3_lib.add_wimax_service_flow(network, install=("Ccatcca", "wimax2"), 
        source=("Urpay", "wifi1", None), dest=("Ccatcca", "wimax2", 9), 
        protocol="udp", direction="down", scheduling="rtps", priority=0)
    
    # Tracing
    #device = network.nodes["Josjojauarina 1"].devices["wifi1"]
    #device.phy_helper.EnablePcap("udp_echo", device.ns3_device)

    # Run simulation    
    ns3_lib.run_simulation(10.0)
    
if __name__ == '__main__':
    sys.exit(ns3_lib.simulation_main(sys.argv[1:], simulation,
        "Run a UDP server/client simple example"))
