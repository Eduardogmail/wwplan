#!/usr/bin/python
import sys
import re

import yaml

import lib
import radiomobile

def bracket_split(s):
    """Split a 's1 [s2]' string into a ('s1', 's2') tuple."""
    match = re.match("^(.*?)\s*\[(.*)\]$\s*", s)
    return (match.groups() if match else (s, None))

def transform(d, properties):
    """
    Yield new pairs from dictionary d based on properties dictionary 
    continaining pairs (key, (new_key, transform_func))."""
    for (k, v) in d.items():
        if k in properties:
            new_name, transform = properties[k]
            transform = transform or (lambda x: x)
            yield (new_name, transform(v))
                          
def get_netinfo_from_report(report):
    """Get netinfo (dictionary) from Radio Mobile report struct."""                    
    output = {}
            
    units = {}
    for unit_name, unit in report.units.iteritems():
        transform_properties = {
            "elevation": ("elevation", None),
            "location_meters": ("location", lambda loc: list(loc)),
        }
        units[unit_name] = dict(transform(vars(unit), transform_properties))
    output["units"] = units
    
    networks = {}
    for net_name, net in report.nets.iteritems():
        short_net_name, smode = bracket_split(net_name)        
        if smode.startswith("wifi"):
            mode = dict(standard="wifi", wifi_mode=smode)
        elif smode.startswith("wimax"):
            sp = smode.split("-")
            standard = "wimax"
            scheduler = ("simple" if len(sp) < 2 else sp[1])
            mode = dict(standard="wimax", wimax_scheduler=scheduler)        
        nodes, terminals = lib.partition(net.net_members.items(),
            lambda (name, member): member.role.lower() in ("node", "master"))
        assert len(nodes) == 1
        def _get_info(name, obj):
            short_system_name, wimax_mode = bracket_split(obj.system)
            d = dict(name=name, system=short_system_name, wimax_mode=wimax_mode)
            return dict((k, v) for (k, v) in d.items() if v)                     
        network_info = {
            "mode": mode,
            "node": _get_info(*nodes[0]),
            "terminals": [_get_info(*terminal) for terminal in terminals],
        }
        networks[short_net_name] = network_info 
    output["networks"] = networks
    
    return output

### Main

def main(args, stream=sys.stdout):
    import optparse
    usage = """Usage: %prog [OPTIONS] RADIOMOBILE_REPORT

    Parse a Radio Mobile report and write the netinfo YML to stdout."""  
    parser = optparse.OptionParser(usage)
    options, args0 = parser.parse_args(args)
    
    if len(args0) != 1:
        parser.print_help()
        return 2
    report_filename, = args0
    report = radiomobile.parse_report(report_filename)
    netinfo = get_netinfo_from_report(report)
    stream.write(yaml.dump(netinfo))    

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
