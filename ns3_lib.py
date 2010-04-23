#!/usr/bin/python
import sys
import ns3
import optparse
import logging

import lib
import ns3_radiomobile

# Generalizate if necessary
def create_througput_gnuplot(monitor_info, flow_id, filename, title, image_format="png"):
    """Create Gnuplot PLT file for a saved FlowStats."""  
    gnuplot = ns3.Gnuplot("%s.%s" % (filename, image_format), title)
    dataset = ns3.Gnuplot2dDataset("Flow %d" % flow_id)
    dataset.SetStyle(ns3.Gnuplot2dDataset.LINES)
    gnuplot.SetLegend("Time (seconds)", "Troughtput (Mbps)")    
    flow_stats_steps = monitor_info["flow_stats_steps"]
    pairs = flow_stats_steps[flow_id]
    dataset.Add(pairs[0][0], 0)
    for (time_x, y) in get_flow_stats_deltas(pairs, "rxBytes"):
        dataset.Add(time_x, 8 * y / 1e6)
    gnuplot.AddDataset(dataset)
    pltfilename = "%s.plt" % filename
    logging.info("created Gnuplot for flow '%d': %s" % (flow_id, pltfilename))
    gnuplot.GenerateOutput(ns3.ofstream(pltfilename))

### Monitoring

def enable_monitor(network, interval=None):
    """
    Enable FlowMonitor and return a structure with state. 
    
    The state must be saved to call other functions in module.        
    """    
    def _ip2info_pairs():
        for node_name, node_attrs in network.nodes.iteritems():
            for device_name, device_attrs in node_attrs.devices.iteritems():
                info = dict(device_name=device_name, node_name=node_name)
                yield str(device_attrs.interfaces[0].address), info
    def _monitor_step(flow_stats_steps):
        """Called every 'interval' seconds. Save flow-stats for later processing."""
        simtime = ns3.Simulator.Now().GetSeconds()            
        for flow_id, flow_stats in monitor.GetFlowStats():
            flow_stats_steps.setdefault(flow_id, []).append((simtime, flow_stats))
        ns3.Simulator.Schedule(ns3.Seconds(interval), _monitor_step, flow_stats_steps)
                
    flowmon_helper = ns3.FlowMonitorHelper()
    monitor = flowmon_helper.InstallAll()
    ip2info = dict(_ip2info_pairs())
    flow_stats_steps = {}
    if interval is not None:
        ns3.Simulator.Schedule(ns3.Seconds(interval), _monitor_step, flow_stats_steps)
    return dict(helper=flowmon_helper, monitor=monitor, 
        ip2info=ip2info, flow_stats_steps=flow_stats_steps)

def get_flow_stats_deltas(pairs, attr):
    for (start_time, fs1), (end_time, fs2) in lib.pairwise(pairs):
        delta = end_time - start_time
        value = (getattr(fs2, attr) - getattr(fs1, attr)) / delta
        yield end_time, value

def print_stats(output, flow_id, flow_stats, flow_stats_steps, show_histograms):
    """
    Return some info (Rx/Tx bytes/packets/throughput, lost packets,
    mean delay/jitter/hopcount values, histograms) for flow-stats objects.
    """ 
    def get_throughput(kind):
        st = flow_stats    
        bytes, tfirst, tlast = {
            "rx": (st.rxBytes, st.timeFirstRxPacket, st.timeLastRxPacket),
            "tx": (st.txBytes, st.timeFirstTxPacket, st.timeLastTxPacket),
        }[kind]
        first, last = [t.GetSeconds() for t in [tfirst, tlast]]        
        return (8.0 * bytes) / (last - first) / 1e6
    
    # Basic info
    st = flow_stats
    output(1, "Tx Bytes: %d" % st.txBytes)
    output(1, "Rx Bytes: %d" % st.rxBytes)
    output(1, "Tx Packets: %d" % st.txPackets)
    output(1, "Rx Packets: %d" % st.rxPackets)
    output(1, "Tx Throughput: %0.2f Mbps" % get_throughput("tx"))
    output(1, "Rx Throughput: %0.2f Mbps" % get_throughput("rx"))
    output(1, "Lost Packets: %d" % st.lostPackets)
    if st.rxPackets > 1:
        output(1, "Mean{Delay}: %.2e" % (st.delaySum.GetSeconds() / st.rxPackets))
        output(1, "Mean{Jitter}: %.2e" % (st.jitterSum.GetSeconds() / (st.rxPackets - 1)))
        output(1, "Mean{Hop Count}: %d" % (float(st.timesForwarded) / st.rxPackets + 1))
        
    if show_histograms:
        histograms = [
            ("Delay Histogram", st.delayHistogram),
            ("Jitter Histogram", st.jitterHistogram),
            ("PacketSize Histogram", st.packetSizeHistogram),
        ]
        for title, attr in histograms: 
            output(1, title)
            for i in range(attr.GetNBins()):
                args = (i, attr.GetBinStart(i), attr.GetBinEnd(i), attr.GetBinCount(i))
                output(2, "%d (%s - %s): %d" % args)

    for reason, drops in enumerate(st.packetsDropped):
        output(1, "Packets dropped by reason %d: %d packets" % (reason, drops))
        
    if flow_id in flow_stats_steps:
        result = ["%s=%s" % (delta, 8.0*value) for (delta, value) in 
                  get_flow_stats_deltas(flow_stats_steps[flow_id], "rxBytes")]
        output(1, "Rx Throughput steps (bps): %s" % ", ".join(result))

def print_monitor_results(monitor_info, show_histograms=False, stream=sys.stdout):
    """Print info about flow stats in simulation."""    
    def output(indent_level, line):
        stream.write(" "*(2*indent_level) + line + "\n")
    monitor = monitor_info["monitor"]
    flow_stats_steps = monitor_info["flow_stats_steps"]
    monitor.CheckForLostPackets()
    classifier = monitor_info["helper"].GetClassifier()
    for flow_id, flow_stats in monitor.GetFlowStats():
        t = classifier.FindFlow(flow_id)
        proto = {6: 'TCP', 17: 'UDP'}.get(t.protocol, "PROTOCOL_UNKNOWN")
        source = monitor_info["ip2info"][str(t.sourceAddress)]
        source_name, source_device = source["node_name"], source["device_name"]
        dest = monitor_info["ip2info"][str(t.destinationAddress)]
        dest_name, dest_device = dest["node_name"], dest["device_name"]
        args = (flow_id, proto, t.sourceAddress, t.sourcePort, source_name, source_device, 
                t.destinationAddress, t.destinationPort, dest_name, dest_device)
        output(0, "Flow %d (%s) - %s/%s (%s:%s) --> %s/%d (%s:%s)" % args)
        print_stats(output, flow_id, flow_stats, flow_stats_steps, show_histograms)
        
def save_monitor_xmldata(monitor_info, filename):
    """Save flow-monitor XML to filename."""
    monitor_info["monitor"].SerializeToXmlFile(filename, True, True)

### Applications
   
def udp_echo_app(network, client_node, server_node, server_device, start, stop, 
                 packets=1, interval=1.0, port=9, packet_size=1024):
    """Set up a UDP echo client/server."""                     
    server = network.nodes[server_node]
    server_address = server.devices[server_device].interfaces[0].address
    echoServer = ns3.UdpEchoServerHelper(port)
    serverApps = echoServer.Install(server.ns3_node)
    serverApps.Start(ns3.Seconds(start))
    serverApps.Stop(ns3.Seconds(stop))

    client = network.nodes[client_node]
    echoClient = ns3.UdpEchoClientHelper(server_address, 9)
    echoClient.SetAttribute("MaxPackets", ns3.UintegerValue(packets))
    echoClient.SetAttribute("Interval", ns3.TimeValue(ns3.Seconds(interval)))
    echoClient.SetAttribute("PacketSize", ns3.UintegerValue(packet_size))
    clientApps = echoClient.Install(client.ns3_node)
    clientApps.Start(ns3.Seconds(start))
    clientApps.Stop(ns3.Seconds(stop))
   
def onoff_app(network, client_node, server_node, server_device, 
              start, stop, rate, port=9, packet_size=1024, 
              access_class=None, ontime=1, offtime=0):
    """Set up a OnOff client + sink server."""                  
    server = network.nodes[server_node]
    server_address = server.devices[server_device].interfaces[0].address
    
    local_address = ns3.InetSocketAddress(ns3.Ipv4Address.GetAny(), port)
    sink_helper = ns3.PacketSinkHelper("ns3::UdpSocketFactory", local_address)

    server_apps = sink_helper.Install(server.ns3_node)
    server_apps.Start(ns3.Seconds (start));
    server_apps.Stop(ns3.Seconds(stop));

    client = network.nodes[client_node]
    remote_address = ns3.InetSocketAddress(server_address, port)
    onoff_helper = ns3.OnOffHelper("ns3::UdpSocketFactory", ns3.Address())
    onoff_helper.SetAttribute("OnTime", ns3.RandomVariableValue(ns3.ConstantVariable(ontime)))
    onoff_helper.SetAttribute("OffTime", ns3.RandomVariableValue(ns3.ConstantVariable(offtime)))
    onoff_helper.SetAttribute("DataRate", ns3.DataRateValue(ns3.DataRate(rate)))
    onoff_helper.SetAttribute("PacketSize", ns3.UintegerValue(packet_size))
    onoff_helper.SetAttribute("Remote", ns3.AddressValue(remote_address))
    
    # Set QoS Access Class -> Tid
    # Note that this only works with a patched OnOffApplication with QosTid attribute
    if access_class is not None:
        access_class_to_qos_tid = {
            "ac_vo": 6, # AC_VO (Tid: 6, 7)
            "ac_vi": 4, # AC_VI (Tid: 4, 5)
            "ac_be": 0, # AC_BE (Tid: 0)
            "ac_bk": 1, # AC_BK (Tid: 1, 2)
            "ac_be_nqos": 3, # AC_BE_NQOS (Tid: 3)
        }
        qos_tid = access_class_to_qos_tid[access_class.lower()]
        onoff_helper.SetAttribute("QosTid", ns3.UintegerValue(qos_tid))
    
    client_apps = onoff_helper.Install(client.ns3_node)    
    client_apps.Start(ns3.Seconds(start))
    client_apps.Stop(ns3.Seconds(stop))

def get_address_from_node(node, device_name, interface_index=0):
    """Return a nd3.Ipv4Address object for the interface in device node."""
    return node.devices[device_name].interfaces[interface_index].address

def add_wimax_service_flow(network, install, source, dest,
        protocol, direction, scheduling, priority):
    """
    Add a WiMax service flow to node for connection (source/port -> dest/port).
    
    protocol: "udp" | "tcp"
    direction: "down" | "up"
    scheduling: "be" | "rtps" | "ugs"
    priority: 0-127    
    """ 
    install_node, install_device = install
    source_node, source_device, source_port = source
    dest_node, dest_device, dest_port = dest           
    network_node = network.nodes[install_node]
    address = network_node.devices[install_device].interfaces[0].address    
    ss_device = network_node.devices[install_device].ns3_device
    assert isinstance(ss_device, ns3.SubscriberStationNetDevice)
    source_address = get_address_from_node(network.nodes[source_node], source_device)
    dest_address = get_address_from_node(network.nodes[dest_node], dest_device)    
    ns3_protocol = {"tcp": 6, "udp": 17}[protocol.lower()]
    sp1, sp2 = ((source_port, source_port) if source_port else (0, 65535))
    dp1, dp2 = ((dest_port, dest_port) if dest_port else (0, 65535))       
    down_link_classifier = ns3.IpcsClassifierRecord(
        source_address, ns3.Ipv4Mask("255.255.255.255"),
        dest_address, ns3.Ipv4Mask("255.255.255.255"),
        sp1, sp2, dp1, dp2, 
        ns3_protocol, priority)
    ns3_direction = getattr(ns3.ServiceFlow, "SF_DIRECTION_" + direction.upper())
    ns3_service_flow = getattr(ns3.ServiceFlow, "SF_TYPE_" + scheduling.upper())
    wimax_helper = network_node.devices[install_device].helper
    down_link_flow = wimax_helper.CreateServiceFlow(ns3_direction,
        ns3_service_flow, down_link_classifier)
    ss_device.AddServiceFlow(down_link_flow)

### Simulation funcions

def run_simulation(stop=None):
    """Run simulation until 'stop' time."""
    if stop:
        ns3.Simulator.Stop(ns3.Seconds(stop))
    ns3.Simulator.Run()
    ns3.Simulator.Destroy()    
   
def simulation_main(args, simulation, help):
    usage = """Usage: %%prog [OPTIONS] radiomobile_report_txt_path

    %s""" % help 
    parser = optparse.OptionParser(usage)
    parser.add_option('-v', '--verbose', dest='vlevel', action="count",
      default=0, help='Increase verbose level)')
    parser.add_option('-n', '--netinfo', dest='netinfo', 
      default=None, help='Use a netinfo YML file')
    options, args0 = parser.parse_args(args)
    
    levels = [logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG]
    level = levels[min(options.vlevel, len(levels)-1)]
    ns3_radiomobile.set_logging_level(level)
    if options.netinfo:
        network = ns3_radiomobile.create_network_from_yaml_file(options.netinfo)
    elif len(args0) == 1:
        report_filename, = args0
        network = ns3_radiomobile.create_network_from_report_file(report_filename)
    else:
        parser.print_help()
        return 2                
    return simulation(network)
