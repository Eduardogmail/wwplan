#!/usr/bin/python
import sys
import optparse
import operator
import pprint
import logging

import yaml

import ns3
import ns3_lib
import network as network_mod

def filter_dict_by_keys(d, reject_keys):
    """Return dictionary with pairs in d except those with keys in 'rejects_keys'"""
    return dict((k, v) for (k, v) in d.iteritems() if k not in reject_keys)
    
def siminfo(filename):
    """Run a simulation YML file."""
    logging.debug("Open simulation file: %s" % filename)
    config = yaml.load(open(filename).read())
    logging.info("Simulation: %s (%s)" % (config["description"], config["version"]))
    logging.debug("Simulation YAML:")
    for line in pprint.pformat(config).splitlines(): 
        logging.debug(line)
        
    assert "netinfo" in config, "missing compulsory variable: netinfo"
    network = network_mod.create_network_from_yaml_file(config["netinfo"])
    
    # Enable Logs    
    for name, string_flags in (config["logs"] or {}).iteritems():
        attrs = ["LOG_" + s.upper() for s in string_flags.split("|")]
        flags = reduce(operator.or_, [getattr(ns3, attr) for attr in attrs])
        logging.debug("Log enabled: %s=%s" % (name, flags))
        ns3.LogComponentEnable(name, flags)
        
    # Add applications
    assert "apps" in config
    for app in config["apps"]:
        available_applications = ns3_lib.get_available_applications()
        assert (app["type"] in available_applications), \
            "Application type '%s' not found, available: %s" % \
            (app["type"], ", ".join(available_applications.keys()))
        app_kwargs = filter_dict_by_keys(app, ["type"])
        app_func = available_applications[app["type"]]
        logging.debug("Add application: %s (%s)" % (app["type"], app_kwargs))
        app_func(network, **app_kwargs)

    for flow in config.get("wimax_service_flows", []):
        logging.debug("Add service flow: %s" % flow)
        ns3_lib.add_wimax_service_flow(network, **flow)
    
    # Enable flow-monitor & tracking    
    interval = config["simulation"].get("interval", 0.1)
    logging.debug("Flow monitor interval: %s seconds" % interval)
    monitor_info = ns3_lib.enable_monitor(network, interval)

    for options in config["results"].get("save_pcap", []):
        device = network.nodes[options["node"]].devices[options["device"]]
        device.phy_helper.EnablePcap(options["filename"], device.ns3_device)
        logging.debug("Enable pcap for %s:%s" % (options["node"], options["device"]))

    # Start simulation        
    duration = config["simulation"].get("duration")
    ns3_lib.run_simulation(network, duration)
            
    # Results
    ns3_lib.print_monitor_results(monitor_info)    
    if "monitor" in config["results"]:
        xmlfile = results["monitor"].get("save_xml")
        if xmlfile:
            ns3_lib.save_monitor_xmldata(monitor_info, xmlfile)

    for plot in config["results"].get("plots", []):
        available_plots = ns3_lib.get_available_plots()
        assert (plot["type"] in available_plots), \
            "Plot type '%s' not found, available: %s" % \
            (plot["type"], ", ".join(available_plots.keys()))
        plot_func = available_plots[plot["type"]]
        plot_kwargs = filter_dict_by_keys(plot, ["type"])
        plot_func(monitor_info, **plot_kwargs)
              
    
def main(args):
    usage = """usage: %prog [options]

    Run a wwplan siminfo YML file.""" 
    parser = optparse.OptionParser(usage)
    parser.add_option('-v', '--verbose', dest='vlevel', action="count",
        default=0, help='Increase verbose level)')
    options, args0 = parser.parse_args(args)
    ns3_lib.set_logging_level(options.vlevel)
    if not args0:
        parser.print_help()
        return 2
    siminfo_path, = args0
    siminfo(siminfo_path)

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
