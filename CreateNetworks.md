# Create a network #

We will use a real example throughout the tutorial to demonstrate the whole process of creation and simulation of a network. The test network is in fact part of a real [EHAS network](http://www.ehas.org/) deployed in the Peruvian Andes near Cusco. Some details of the network:

  * It has 7 units/nodes: Josjojauarina1, Josjojauarina2, Ccatcca, Kcauri, Urpay, Huiracochan, Urcos.

  * It has 4 sub-networks: Josjojauarina2-Ccatcca-Kcauri (WiMAX), Josjojauarina1-Josjojauarina2 (WiFi), Josjojauarina1-Urpay-Huiracochan (WiFi), Huiracochan-Urcos (WiFi).

For the impatient, the Radio Mobile network file can be downloaded from the repository: [josjo.net](http://wwplan.googlecode.com/hg/examples/josjo.net).

### Map and units ###

  * First create the nodes (_units_, in Radio Mobile terminology):

_File_ -> _Unit properties_

![http://wiki.wwplan.googlecode.com/hg/img/rmw-units.png](http://wiki.wwplan.googlecode.com/hg/img/rmw-units.png)

  * Configure the map properties so it uses SRTM info to draw the map:

_File_ -> _Map properties_

![http://wiki.wwplan.googlecode.com/hg/img/rmw-map-properties.png](http://wiki.wwplan.googlecode.com/hg/img/rmw-map-properties.png)

  * Now you should be able to see the units located on the map:

![http://wiki.wwplan.googlecode.com/hg/img/rmw-map.png](http://wiki.wwplan.googlecode.com/hg/img/rmw-map.png)

### Networks and systems ###

One the units are placed onto the map, we specify the sub-networks and systems (type of interface).

We create the four networks and use its name to include information that will be lated used in the simulation. Set the network name and the network type (between brackets) using the following convention:

| **Mode** | **Network string** | **Accepted values** |
|:---------|:-------------------|:--------------------|
| WiFi     | [ns-3 mode](http://www.nsnam.org/doxygen-release/classns3_1_1_wifi_mode.html) | wifia-XYmbs (XY=6, 9, 12, 18, 24, 36, 48, 54), wifib-XYmbs (XY= 1, 2, 5.5, 11) |
| WiMAX    | _wimax_-_[scheduler](http://www.nsnam.org/doxygen-release/classns3_1_1_wimax_helper.html#a27a40a8f601900126156781c2ca79406)_  | wimax-simple, wimax-rtps, wimax-mbqos |

_File_ -> _Network properties_

![http://wiki.wwplan.googlecode.com/hg/img/rmw-networks.png](http://wiki.wwplan.googlecode.com/hg/img/rmw-networks.png)

WiFi 802.11 mode is common for all nodes, but WiMAX interfaces may use different modulations for each Subscriber Station. Thus, the system name must carry that info. The available [WiMAX modulations](http://www.nsnam.org/doxygen-release/classns3_1_1_wimax_phy.html) are:
BPSK\_12, QPSK\_12, QPSK\_34, QAM16\_12, QAM16\_34, QAM64\_23, QAM64\_34.

| **Mode** | **Modulation** |
|:---------|:---------------|
| WiMAX    | BPSK\_12, QPSK\_12, QPSK\_34, QAM16\_12, QAM16\_34, QAM64\_23, QAM64\_34, all (for Base Stations) |

![http://wiki.wwplan.googlecode.com/hg/img/rmw-systems.png](http://wiki.wwplan.googlecode.com/hg/img/rmw-systems.png)

Lastly, we need to define the topology of the network. Set role to _Master_ for _Access Points_ (WiFi) or _Base Stations_ (WiMAX), and _Slave_ for _Stations_ (WiFi) and _Subscriber Stations_ (WiMAX):

![http://wiki.wwplan.googlecode.com/hg/img/rmw-membership.png](http://wiki.wwplan.googlecode.com/hg/img/rmw-membership.png)

### Create the report ###

Extract all the relevant information of the network saving a text-file network report.

_Tools_ -> _Network report_ -> _File_

![http://wiki.wwplan.googlecode.com/hg/img/rmw-report.png](http://wiki.wwplan.googlecode.com/hg/img/rmw-report.png)

## Convert the network report ##

The network report (_report.txt_) created by Radio Mobile must be converted into a NetInfo report to be used in out simulations. But before we need to enable the Python bindings for ns-3; the easiest way of doing it is running the shell:

```
$ ./waf shell
Waf: Entering directory `/home/arnau/ehas/wimax/build'
Waf: Leaving directory `/home/arnau/ehas/wimax/build'
```

You must add (only once) _wwplan_ in _PYTHONPATH_ :

```
$ export PYTHONPATH=$PYTHONPATH:wwplan/
```

And now convert the report to a NetInfo file:

```
$ python wwplan/wwplan/netinfo.py report.txt > netinfo.yml
```

Take a look at the generated YAML file. From now on this is the file we will use in out ns-3 simulations, so you can modify it directly (see [YAML format](http://en.wikipedia.org/wiki/YAML) for details).