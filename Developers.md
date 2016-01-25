# Checkout the repository #

To get the source:
$ cd ns-3-dev/
$ hg clone https://wwplan.googlecode.com/hg/ wwplan 
}}

= Scripts =

The core of _wwplan_ are the [http://code.google.com/p/wwplan/source/browse/wwplan set of scripts] used to interface Radio Mobile and ns-3:

 * *wwplan/odict.py*: [http://docs.python.org/tutorial/datastructures.html#dictionaries Python dictionaries] (map hashes) are unordered. However, some structs in the Radio Mobile report (units, networks) are kept in order, so this module adds a new ordered dictionary type (*odict*).

 * *wwplan/lib.py*: Generic functions that will be used by all other modules. 

 * *wwplan/netinfo.py*: Convert a Radio Mobile report to !NetInfo YML. It can be called from the command line:

{{{
$ cd ns-3-dev
$ python wwplan/wwplan/netinfo.py report.txt 
}}}

 * *wwplan/network.py*: Contains functions to build !WiFi and WiMAX networks in ns-3 from !NetInfo structs.

 * *wwplan/ns3_lib.py*: ns-3 specific functions. It currently implements plotting (_throughput_), applications (_udp_echo_ and _onff_), print_stats function, and WiMAX service flows.

 * *wwplan/run_siminfo.py*: Run a !SimInfo file:

{{{
$ cd ns-3-dev
$ python wwplan/wwplan/run_siminfo.py mysiminfo.yml 
}}}

== Run tests ==

You can run the whole [http://code.google.com/p/wwplan/source/browse/tests suite of tests] this way:

{{{
$ cd ns-3-dev/wwplan
$ ./run_tests.sh
}}}

= Examples = 

The [http://code.google.com/p/wwplan/source/browse/examples examples files] contain the network discussed in the tutorial:

 * *examples/josjo.net*: Radio Mobile .net file.
 * *examples/josjo.report.txt*: Radio Mobile report text file generated from josjo.net.
 * *examples/josjo.netinfo.yml*: !NetInfo file generated with wwplan/netinfo.py
 * *examples/onoff.py*: Python script of onoff simulation.
 * *examples/udp_echo.py*: Python script of udp_echo simulation.
 * *examples/udp_echo.siminfo.yml*: !SimInfo file for udp_echo simulation.
  
= Patches =

The _onoff_ applications has an optional _access_class_ parameter which cannot be modified in the standard onoff applicaction. So if we want to use we'll need to [http://code.google.com/p/wwplan/source/browse/patches patch] ns-3 sources. We basically add a new attribute (_!QosTid_) and tag the packet to send if attribute was set.

To generate the patch:

{{{
$ cd ns-3-dev/wwplan
$ ./create_ns3_patch.sh
}}}
```