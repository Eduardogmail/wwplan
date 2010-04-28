"""
Interface module between Radio Mobile and ns-3.

The struct 'Network' has the following attributes:
    
    * nodes: dictionary of nodes with pairs (name, node_attributes). Node attributes:
        * ns3_node: ns3.Node object for the node.
        * location: (x, y) in meters.
        * devices: dictionary of devices with pairs (name, device_attributes). Device attributes:
            * ns3_device: ns3.NetDevice object for this device.
            * helper: WiFi or WiMax helper used to create the device.
            * phy_helper: WiFi or WiMax PHY Helper used to create the device.
            * interfaces: List of ns3.Ipv4Addresss objects attached to device.
            
    * networks: dictionary of networks with pairs (name, network_struct). Network struct attributes:
        * node: Node name.
        * terminal: List of terminals name. 

Examples:
            
>>> network = create_network_from_report_file("myreport.txt")
>>> network.nodes["Urcos"].devices
>>> network.nodes["Urcos"].devices["wifi1"].ns3_device
>>> network.networks["Huiracochan"].terminals
"""
import sys
import re
import logging
import math
from pprint import pprint, pformat

import yaml
import ns3

from wwplan import lib
from wwplan import radiomobile
import wwplan.netinfo
                                         
def set_logging_level(level, format='%(levelname)s -- %(message)s'):
    """Set logging level (DEBUG, WARNING, INFO, ERROR) and message format."""
    logging.basicConfig(level=level, format=format)
   
def get_max_distance_in_network(nodes, node_member, terminal_members):
    """Get maximum distance between node and terminals."""
    def get_distance(t1, t2):
        x1, y1 = t1
        x2, y2 = t2
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)     
    node_location = nodes[node_member].location    
    return max(get_distance(nodes[terminal_member].location, node_location) 
               for terminal_member in terminal_members)

def get_device_key(net, system):
    return net + "-" + system
    
def add_device_to_node(node, short_net_name, network, ns3_device, helper=None, phy_helper=None):
    """Add a ns-3 device to a node structure."""
    attributes = network[node.name]
    device_key = get_device_key(short_net_name, attributes["system"])
    device = lib.Struct("Device", ns3_device=ns3_device, helper=helper,
        phy_helper=phy_helper, interfaces=[], wimax_flow_services=[])
    node.devices[device_key] = device
    
def add_interface_to_device_node(node, short_net_name, network, address):
    """Add a ns-3 interface (address) to node.devices[system_name].interfaces."""
    attributes = network[node.name]
    device_key = get_device_key(short_net_name, attributes["system"])
    interface = lib.Struct("Interface", address=address)
    logging.info("Add interface to node %s (%s)" % (node.name, str(address)))
    node.devices[device_key].interfaces.append(interface)

def set_wifi_timeouts(device, max_distance):
    """
    Set MacPropagationDelay and timeouts (AckTimeout, SlotTimeout, CtsTimeout) 
    in a Wifi device suitable for a given distance.
    """
    max_propagation_delay = max_distance / 3e8
    mac = device.GetMac()
    mac.SetMaxPropagationDelay(ns3.Seconds(max_propagation_delay))
    ack_timeout = ns3.Seconds(mac.GetEifsNoDifs().GetSeconds() +
        mac.GetSlot().GetSeconds() + max_propagation_delay * 2)
    ack_timeout = ns3.Time(ns3.NanoSeconds(int(ack_timeout.GetNanoSeconds())))
    mac.SetAckTimeout(ack_timeout)
    mac.SetCtsTimeout(ack_timeout)
    slot_time = ns3.NanoSeconds(mac.GetSlot().GetNanoSeconds() + 
        mac.GetMaxPropagationDelay().GetNanoSeconds() * 2)
    mac.SetSlot(slot_time)

def wifi_network(network_info, net_index, short_net_name, ns3_mode, nodes, 
                 get_node_from_ns3node, node_member, terminal_members):
    """Configure a WiFi network (1 AP - n STAs)."""                    
    max_distance = get_max_distance_in_network(nodes, node_member, terminal_members)
                        
    logging.info("Network '%s': AP-node = '%s', STA-nodes = %s" % 
        (short_net_name, node_member, terminal_members))
    logging.info("Network '%s': ns-3 mode: %s, max_distance: %d meters" %
        (short_net_name, ns3_mode, max_distance))
        
    # Wifi channel
    channel = ns3.YansWifiChannelHelper.Default()
    phy = ns3.YansWifiPhyHelper.Default()        
    channel = ns3.YansWifiChannelHelper.Default()
    channel.SetPropagationDelay("ns3::ConstantSpeedPropagationDelayModel")
    channel.AddPropagationLoss("ns3::FixedRssLossModel", "Rss", ns3.DoubleValue(0))
    phy.SetChannel(channel.Create())

    address_helper = ns3.Ipv4AddressHelper()
    netaddr = "10.1.%d.0" % net_index
    address_helper.SetBase(ns3.Ipv4Address(netaddr), ns3.Ipv4Mask("255.255.255.0"))    
    
    def configure_node(wifi_helper, name):
        ns3_node = nodes[name].ns3_node
        sta_device = wifi_helper.Install(phy, mac, ns3_node)
        node = get_node_from_ns3node(ns3_node)
        add_device_to_node(node, short_net_name, network_info, sta_device.Get(0), 
            helper=wifi_helper, phy_helper=phy)
        set_wifi_timeouts(sta_device.Get(0), max_distance)
        sta_interface = address_helper.Assign(sta_device)
        address = sta_interface.GetAddress(0)
        add_interface_to_device_node(node, short_net_name, network_info, address)
            
    # STA devices & and interfaces    
    wifi_helper = ns3.WifiHelper.Default()
    
    wifi_helper.SetRemoteStationManager ("ns3::ConstantRateWifiManager",
        "DataMode", ns3.StringValue(ns3_mode),
        "RtsCtsThreshold", ns3.StringValue("2200"))
            
    mac = ns3.NqosWifiMacHelper.Default()   
    ssid = ns3.Ssid("%s%d" % (short_net_name[:5], net_index))
    mac.SetType("ns3::QstaWifiMac", 
        "Ssid", ns3.SsidValue(ssid),
        "ActiveProbing", ns3.BooleanValue(False))
        
    for terminal_member in terminal_members:
        configure_node(wifi_helper, terminal_member)
                    
    # AP devices & interfaces
    wifi_helper = ns3.WifiHelper.Default()
    mac = ns3.NqosWifiMacHelper.Default()
    mac.SetType ("ns3::QapWifiMac", 
        "Ssid", ns3.SsidValue(ssid),
        "BeaconGeneration", ns3.BooleanValue(True),
        "BeaconInterval", ns3.TimeValue(ns3.Seconds(2.5)))        
    configure_node(wifi_helper, node_member)

def wimax_network(network_info, net_index, short_net_name, nodes, 
                  get_node_from_ns3node, node_member, terminal_members,
                  scheduler=ns3.WimaxHelper.SCHED_TYPE_RTPS):
    """Configure a WiMax network (1 BS - n SSs)."""                      
    logging.info("Network '%s': BS-node = '%s', SS-nodes = %s" % 
        (short_net_name, node_member, terminal_members))
        
    channel = ns3.SimpleOfdmWimaxChannel(ns3.SimpleOfdmWimaxChannel.FRIIS_PROPAGATION)
    wimax_helper = ns3.WimaxHelper()

    address_helper = ns3.Ipv4AddressHelper()
    netaddr = "10.1.%d.0" % net_index
    address_helper.SetBase(ns3.Ipv4Address(netaddr), ns3.Ipv4Mask("255.255.255.0"))
    
    def configure_node(name, device_type):
        ns3_node = nodes[name].ns3_node
        # Change BW in PHY? (we'd need phy as parameter, not phy_type)
        device = wimax_helper.Install(ns3_node, device_type,
            ns3.WimaxHelper.SIMPLE_PHY_TYPE_OFDM, channel, scheduler)
        node = get_node_from_ns3node(ns3_node)
        if device_type == ns3.WimaxHelper.DEVICE_TYPE_SUBSCRIBER_STATION:
            system_name = network_info[name]["system"]
            wimax_mode = network_info[name]["wimax_mode"]
            # MODULATION_TYPE_XYZ: BPSK_12, QPSK_12, QPSK_34, QAM16_12, 
            #                      QAM16_34, QAM64_23, QAM64_34
            modtype = getattr(ns3.WimaxPhy, "MODULATION_TYPE_" + wimax_mode.upper())
            device.SetModulationType(modtype)
        add_device_to_node(node, short_net_name, network_info, device, helper=wimax_helper)
        container = ns3.NetDeviceContainer()
        container.Add(device)
        interface = address_helper.Assign(container)
        address = interface.GetAddress(0)
        add_interface_to_device_node(node, short_net_name, network_info, address)
        if device_type != ns3.WimaxHelper.DEVICE_TYPE_SUBSCRIBER_STATION:
            return
        #return # uncomment this to configure a default UDP down-link service flow
        
    for terminal_member in terminal_members:
        configure_node(terminal_member, ns3.WimaxHelper.DEVICE_TYPE_SUBSCRIBER_STATION)
                    
    configure_node(node_member, ns3.WimaxHelper.DEVICE_TYPE_BASE_STATION)

def create_network(netinfo):
    """Create a network Struct from a RadioMobile parsed text report."""
    nodes = {}
    for name, attrs in netinfo["units"].iteritems():
        node = lib.Struct("Node", 
            name=name,
            location=attrs["location"], 
            ns3_node=ns3.Node(), 
            devices={})
        nodes[name] = node
        
    ns3node_to_node = dict((node.ns3_node.GetId(), node) for node in nodes.values())
    def get_node_from_ns3node(ns3_node):
        return ns3node_to_node[ns3_node.GetId()]

    # Internet stack
    stack = ns3.InternetStackHelper()
    for name, node in nodes.iteritems():
        stack.Install(node.ns3_node)
    
    networks = {}
    for net_index, (net_name, network) in enumerate(netinfo["networks"].iteritems()):
        # Nodes
        node = network["node"]
        node_member = node["name"]        
        terminal_members = [terminal["name"] for terminal in network["terminals"]]  
        ap_node = nodes[node_member].ns3_node
        sta_nodes = ns3.NodeContainer()            
        for name in terminal_members:
            sta_nodes.Add(nodes[name].ns3_node)
        
        networks[name] = lib.Struct("network", node=node_member, terminals=terminal_members)
        mode = network["mode"]
        network_info = dict((d["name"], d) for d in [network["node"]] + network["terminals"])

                     
        if mode["standard"].startswith("wifi"):
            wifi_network(network_info, net_index, net_name, mode["wifi_mode"], nodes, 
                         get_node_from_ns3node, node_member, terminal_members)
        elif mode["standard"].startswith("wimax"):
            scheduler = getattr(ns3.WimaxHelper, "SCHED_TYPE_" + mode["wimax_scheduler"].upper())
            wimax_network(network_info, net_index, net_name, nodes, 
                          get_node_from_ns3node, node_member, terminal_members,
                          scheduler)
        else:
            raise ValueError, ("Network name must be 'name [wifi_with_ns3_mode" +
                              "| wimax-scheduler]': %s") % ns3_mode

        # Mobility
        mobility = ns3.MobilityHelper()
        mobility.SetMobilityModel("ns3::ConstantPositionMobilityModel")
                                                        
        for member in [node_member] + terminal_members:
            node = nodes[member]
            allocator = ns3.ListPositionAllocator()
            position = tuple(node.location) + (0,) 
            #position = (0, 0, 0)
            allocator.Add(ns3.Vector(*position))
            mobility.SetPositionAllocator(allocator)
            mobility.Install(node.ns3_node)
    
    ns3.Ipv4GlobalRoutingHelper.PopulateRoutingTables()    
    return lib.Struct("Network", nodes=nodes, networks=networks)

def create_network_from_report_file(filename):
    """Create a network Struct from a RadioMobile text-report filename."""
    report = radiomobile.parse_report(filename)
    netinfo = wwplan.netinfo.get_netinfo_from_report(report)
    logging.debug("Netinfo YML contents:")
    for line in yaml.dump(netinfo).splitlines():
        logging.debug("Netinfo: %s" % line.rstrip())
    return create_network(netinfo)

def create_network_from_yaml_file(yamlfile):
    """Create a network Struct from a YAML netinfo file."""
    netinfo = yaml.load(open(yamlfile).read())
    return create_network(netinfo)
