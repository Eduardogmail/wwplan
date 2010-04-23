#!/usr/bin/python
# -*- coding: utf-8 -*
"""
Parse a Radio Mobile report.txt file and return a network Struct:
  
Network Struct attributes:
  - units: Ordered dictionary of units
  - systems: Ordered dictionary of systems
  - nets: Ordered dictionary of sub-networks      

>>> report = parse_report("myreport.txt")
>>> report.units["Urcos"]
>>> report.systems["wifi1"]
>>> report.nets["Josjo1 [wifia-6mbs]"]
"""
import re
import sys
from datetime import datetime
import math

import lib
from odict import odict

def get_distance(origin, destination):
    """
    Calculate distance (in meters) between two WGS84 coordinates using 
    Haversine formula.
    """
    lat1, lon1 = origin
    lat2, lon2 = destination
    radius = 6371
    sin, cos, rad = math.sin, math.cos, math.radians
    dlat = rad(lat2 - lat1)
    dlon = rad(lon2 - lon1)
    a = sin(dlat/2)**2 + (cos(rad(lat1)) * cos(rad(lat2)) * sin(dlon/2)**2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = radius * c
    return int(1000.0 * d)

def get_position_from_reference(coordinates, reference):
    """
    Get relative position of coordinates given a reference.
    
    It uses the local, flat earth approximation. See:        
    http://williams.best.vwh.net/avform.htm#flat
    """
    lat, lon = map(math.radians, coordinates)
    lat0, lon0, r1, r2 = reference
    x = int(round(r2 * math.cos(lat0) * (lon -lon0)))
    y = int(round(r1 * (lat - lat0)))
    return (x, y)

def get_reference(coordinates):
    """Calculate R1/R2 reference values to calculate relative positions."""
    lat0, lon0 = map(math.radians, coordinates)
    a = 6378137
    f = 1 / 298.257223563
    e2 = f * (2 - f)     
    r1 = (a * (1 - e2)) / ((1 - e2 * (math.sin(lat0))**2)**(3.0/2))
    r2 = a / math.sqrt(1 - e2 * (math.sin(lat0))**2)
    return (lat0, lon0, r1, r2)

# Radiomobile functions

def get_lat_lon_from_string(line):
    """
    Return tuple (latitude, longitude) for a coordinates string.
    
    Example of line: "13°31'52"S 071°55'49"W"
    """
    def _string_to_float(string):
        h, m, s, section = re.match("(\d+).*?(\d+).*?(\d+).*?([NSWE])", string).groups()
        value = float(h) + (float(m) / 60.0) + (float(s) / 3600.0)
        return (value if section in ('N', 'E') else -value)
    lat, lon = map(_string_to_float, line.split()[:2])
    return (lat, lon)  

def get_distance_between_locations(location1, location2):
    """Get distance (meters) between two locations (string in lat/long format)."""
    coord1 = get_lat_lon_from_string(location1) 
    coord2 = get_lat_lon_from_string(location2)
    return get_distance(coord1, coord2)

def create_odict_from_items(name, key, dictlst):
    """Construct an ordered dictionary from a list of dictionaries."""
    def _generator():
        for delement in dictlst:        
            dvalues = dict((k, v) for (k, v) in delement.iteritems())
            yield (delement[key], lib.Struct(name, **dvalues))
    return odict(_generator())      
    
def parse_header(lines):
    """
    Check that the headers contain a valid RadioMobile identifier and return
    the generation report date.
    """     
    if len(lines) != 3:
        raise ValueError, "Unknown header: %s" % lines
    metadata, title, generated_on = lines
    expected_title = "Radio Mobile" 
    if title != expected_title:
        raise ValueError, "Unknown header title: %s (expected: %s)" % (title, expected_title)
    info = " ".join(generated_on.split()[-3:])
    return datetime.strptime(info, "%H:%M:%S on %m-%d-%Y")

def parse_active_units(lines):
    """Return ordered dict containing (name, attributes) pairs for units."""
    headers = ["Name", "Location", "Elevation"]
    units = create_odict_from_items("unit", "name", lib.parse_table(lines, headers))
    if units:
        for name, unit in units.iteritems():
            coords = get_lat_lon_from_string(unit.location)
            units[name].location_coords = coords
            elevation = int(float(re.match("([\d.]+)", unit.elevation).group(1)))
            units[name].elevation = elevation 
        unit1 = units.itervalues().next()
        reference = get_reference(unit1.location_coords)
        for name, unit in units.iteritems():
            units[name].location_meters = \
                get_position_from_reference(unit.location_coords, reference)        
    return units
            
def parse_systems(lines):
    """Return orderect dict containing (name, attributes) pairs for systems."""
    headers = ["Name", "Pwr Tx", "Loss", "Loss (+)", "Rx thr.", "Ant. G.", "Ant. Type"]
    return create_odict_from_items("system", "name", lib.parse_table(lines, headers))

def get_net_links(rows, grid_field, units):
    """Parse a quality grid and return dictionary with information.""" 
    def get_quality(lst):
        s = "".join(lst).strip()
        return (int(s) if s else None)
    def clean_node(node):
        items = dict((k, v) for (k, v) in node.iteritems() if not k.startswith("#"))
        return lib.Struct("Node", **items)
    
    for nrow, row in enumerate(rows[:-1]):
        qualities = map(get_quality, lib.grouper(3, row[grid_field][3:], ''))
        for npeer_row, quality in enumerate(qualities):
            if not quality or nrow >= npeer_row:
                continue
            peer_row = rows[npeer_row]
            node1, node2 = map(clean_node, [row, peer_row])
            location1 = units[node1.net_members].location
            location2 = units[node2.net_members].location
            distance = get_distance_between_locations(location1, location2)
             
            link = {            
                "quality": quality,
                "node1": node1,
                "node2": node2,
                "distance": distance,
            }
            yield link

def parse_active_nets(lines, units):
    """Return an orderd dict with nets, each containing a list of links.""" 
    nets_lines = list(lib.split_iter_of_consecutive(lines[1:], lambda s: not s.strip(), 2))
    nets = odict()
    for net_lines in lib.strip_iter_items(nets_lines):
        info = lib.strip_list(net_lines)
        name = info[0].strip()
        block = list(lib.iter_block(lib.strip_list(info[1:]), 
          r"Net members:", r"\s.*Quality ="))
        table, quality_line = block[:-2], block[-1]
        max_quality = int(re.search("Quality = (\d+)", quality_line).group(1))
        grid_field = re.match("Net members:\s*(.*?)\s*Role:", table[0]).group(1)
        grid_fields = ["Net members:", grid_field, "Role:", "System:", "Antenna:"]    
        rows = list(lib.parse_table(table, grid_fields, lambda s: not s.startswith('#')))
        net_members = create_odict_from_items("net_member", "net_members", rows)        
        links = []
        for link in get_net_links(rows, grid_field, units):
            peers = (link["node1"].net_members, link["node2"].net_members)
            link = lib.Struct("Link", 
                peers=peers, 
                quality=link["quality"], 
                distance=link["distance"])
            links.append(link)
        nets[name] = lib.Struct("Network", name=name, 
            net_members=net_members,
            links=links, 
            max_quality=max_quality)
    return nets                

def get_units_for_network(net, role=None):
    """Return units of a network with an (optional) role."""
    def _generator():
        for net_member, attrs in net.net_members.iteritems():
            if role is None or role == attrs.role:
                yield net_member
    return list(_generator())
                                
def parse_report(filename):
    """
    Read and parse a Radiomobile report.txt file.
    
    >>> report = parse_report("report.txt")
    >>> report.nets
    >>> report.systems
    >>> report.units
    """
    lines = open(filename).read().splitlines()
    splitted_lines = list(lib.split_iter(lines, 
      lambda s: s.startswith("---"), skip_sep=True))
    generated_on = parse_header(splitted_lines[0])
    sections = dict((lib.keyify(key[0]), val) for (key, val) in 
      lib.grouper(2, splitted_lines[1:]))
    
    units = parse_active_units(sections["active_units_information"])
    report = lib.Struct("RadioMobileReport",
        generated_on=generated_on,
        general_information=sections["general_information"],
        units=units,
        systems=parse_systems(sections["systems"]),
        nets=parse_active_nets(sections["active_nets_information"], units))
    return report

def main(args):    
    """Print basic information of a report.txt."""
    import os
    import yaml
    if len(args) != 1:
        sys.stderr.write("Usage: %s REPORT_TXT_PATH\n" % os.path.basename(sys.argv[0]))
        return 2
    text_report_filename, = args
    report = parse_report(text_report_filename)
    sys.stdout.write(yaml.dump(report))

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
