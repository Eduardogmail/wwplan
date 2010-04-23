#!/usr/bin/python
import sys
import ns3
import ns3_lib

DESCRIPTION = "Run a OnOff client + sink server example"

def simulation(network):
    ns3.LogComponentEnable("PacketSink", ns3.LOG_LEVEL_ALL | ns3.LOG_PREFIX_TIME)
    
    # Applications    
    ns3_lib.onoff_app(network, client_node="Urcos", 
        server_node="Huiracochan", server_device="wifi1", 
        start=1.0, stop=9.0, rate="1Mbps", access_class="ac_vo")
    ns3_lib.onoff_app(network, client_node="Urpay", 
        server_node="Ccatcca", server_device="wimax2", start=1.0, stop=9.0, rate="0.5Mbps")
    ns3_lib.add_wimax_service_flow(network, install=("Ccatcca", "wimax2"), 
        source=("Urpay", "wifi1", None), dest=("Ccatcca", "wimax2", 9), 
        protocol="udp", direction="down", scheduling="rtps", priority=0)

    # Tracing    
    #device = network.nodes["Josjojauarina 1"].devices["wifi1"]
    #device.phy_helper.EnablePcap("onoff", device.ns3_device)

    monitor_info = ns3_lib.enable_monitor(network, interval=0.1)
    
    # Run simulation
    ns3_lib.run_simulation(3.0)
    ns3_lib.print_monitor_results(monitor_info)
    ns3_lib.save_monitor_xmldata(monitor_info, "onoff.flowmon.xml")
    ns3_lib.create_througput_gnuplot(monitor_info, 1, "Urcos-Huiracochan 1Mbps", "Josjo network")
    
if __name__ == '__main__':
    sys.exit(ns3_lib.simulation_main(sys.argv[1:], simulation, DESCRIPTION))
