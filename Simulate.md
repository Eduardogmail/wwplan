# Simulate a network #

We have two different ways of running simulations: using a Python script or running SimInfo YML files. Let's see both of them.

## Simulate with Python scripts ##

If you feel comfortable with Python this is the more versatile way to go, as you free to tweak with ns-3 directly. Take a look at the examples: [udp\_echo.py](http://wwplan.googlecode.com/hg/examples/udp_echo.py) and [onoff.py](http://wwplan.googlecode.com/hg/examples/onoff.py).

To run a Python simulation:

```
$ python wwplan/examples/udp_echo.py wwplan/examples/josjo.netinfo.yml
```

## Simulate using SimInfo files ##

Take a look at the example:

http://wwplan.googlecode.com/hg/examples/udp_echo.siminfo.yml

A SimInfo is a YML file with the following variables:

  * _description_ (string): Explain succinctly what this simulation does.

  * _version_ (string): Make sure to increment the version each time you modify the file.

  * _netinfo_ (string): Path to netinfo file containing the network to simulate with.

  * _simulation_ (map):
    * _duration_ (float): Total duration of simulation (seconds)

  * _logs_ (map): Keys (string) of the map specify which logs must be enabled. These strings are defined by ns-3 components (using the _NS\_LOG\_COMPONENT\_DEFINE_ macro). The values (string) define the log level. See the [Logging section](http://www.nsnam.org/docs/tutorial/tutorial_21.html#Using-the-Logging-Module) in the tutorial.

  * _wimax\_service\_flows_ (list): Add a [WiMAX QoS service flow](http://www.nsnam.org/doxygen-release/classns3_1_1_service_flow.html). If a Subscriber Station has no service flow  specified  a default one (for UDP and all sources and ports) will be created. Each element of this list contain a map with the following entries:
    * _install_ (list): ` [Node, DeviceName] `. Node and DeviceName where the service flow must be configured.
    * _source_ (list): {{ Node, DeviceName, Port] }}}. Node, DeviceName and Port of the source of the flow.
    * _dest_ (list): ` [Node, DeviceName, Port] `. Node, DeviceName and Port of the destination of the flow.
    * _protocol_ (string): Protocol (_udp_ or _tcp_).
    * _direction_ (string): Service flow direction: _down_ or _up_.
    * _scheduling_ (string): Scheduling type for the service flow. See [API](http://www.nsnam.org/doxygen-release/classns3_1_1_wimax_helper.html#a27a40a8f601900126156781c2ca79406). Accepted values: _simple_, _rtps_, _mbqos_.
    * _priority_ (8-bit integer): Priority of service flow. See [API](http://www.nsnam.org/doxygen-release/classns3_1_1_service_flow.html).

  * _applications_ (list): List of applications to run in the simulation. Each element of the list contains a map with the following entries:
    * _type_ (string): Application type. Currently implemented: _udp\_echo_, _onoff_.
    * _start_ (float): Time to start the application (seconds).
    * _stop_ (float): Time to stop the application (seconds).

  * _udp\_echo_ - _client\_node_ (string): Node of the client (who sends the ping).
  * _udp\_echo_ - _server\_node_ (string): Node of the server (who received the ping and replies).
  * _udp\_echo_ - _server\_device_ (string): DeviceName of the server.
  * _udp\_echo_ - _packet\_size_ (integer): Packet size.
  * _udp\_echo_ - _packets_ (integer): How many packets to send.
  * _udp\_echo_ - _interval_ (integer): Interval (seconds) between packets.

  * _onoff_ - _client\_node_ (string): Node of the client (who sends the traffic).
  * _onoff_ - _server\_node_ (string): Node of the server (who receives the traffic) in a sink (see [manual](http://www.nsnam.org/docs/manual/manual_40.html#Overview) and [tutorial](http://www.nsnam.org/docs/tutorial/tutorial_23.html#Using-the-Tracing-System) for more info).
  * _onoff_ - _server\_device_ (string): DeviceName of the server.
  * _onoff_ - _packet\_size_ (integer): Packet size.
  * _onoff_ - _rate_ (string): Rate of traffice. Use ns-3 [DataRate](http://www.nsnam.org/doxygen/index.html) strings.
  * _onoff_ - _interval_ (integer): Interval (seconds) between consecutive packets sendings.
  * _onoff_ - _access\_class_ (string): Access class used to tag the packages. See the [correspondence between access class (AC\_\* values) and Tid values](http://www.nsnam.org/doxygen/group___wifi.html). This option can only be used for patched ns-3 (as explained in Install section). Accepted values: _AC\_VO_, _AC\_VI_, _AC\_BE_, _AC\_BK_, _AC\_BE\_NQOS_.

  * _results_ (map):
    * _flowmonitor_ (map):
      * _save\_xml_ (string): Path to save the flow-monitor results in XML format. See [FlowMonitor API](http://www.nsnam.org/doxygen-release/classns3_1_1_flow_monitor.html).
    * _save\_pcap_ (list): List of _pcap_ files to save. Each element is a map with entries:
      * _filename_ (string): Path of the _pcap_ file.
      * _node_ (string): Node name where the pcap will be saved for.
      * _device_ (string): Device name where the pcap will be saved for.

  * _plots_ (list): List of plots ([GnuPlot](http://gnuplot.sourceforge.net/) format) to create.
    * _title_ (string): Main title of the plot.
    * _type_ (string): Type of the plot. Currently implemented: _throughput_.
    * _filename_ (string): Base filename for the _plt_ and _png_ files to create.
    * _flow\_ids_ (list): List of flow identifiers (beginning from 1) to include in the plotting.

To run a SimInfo file:

```
$ python wwplan/wwplan/run_siminfo.py wwplan/examples/udp_echo.siminfo.yml
```

To create an image from a PLT file:

```
$ gnuplot udp_echo-throughput.plt
$ display udp_echo-throughput.png
```

To inspect [pcap](http://en.wikipedia.org/wiki/Pcap) files you can use [tcpdump](http://www.tcpdump.org/) or [wireshark](wireshark.md).

```
$ wireshark file.pcap
```

# Some notes #

## Device names ##

Node and DeviceName are widely used on simulations. Node name has no secret, is directly the unit name taken from the Radio Mobile report. The DeviceName is a bit more complicated. System names in Radio Mobile do not define an specific system but a **class**. This means that two different nodes can use the same system. Even more, the same node can use the same system for different links. So clearly we cannot use solely the system name to identify a device, we need also the network. The DeviceName includes a concatenation of the network name and the system name (with a hyphen: **-**):

| **RMW Network name** | **RMW System name** | **DeviceName in simulations** |
|:---------------------|:--------------------|:------------------------------|
| Josjo1               | wifi1               | Jojo1-wifi2                   |
| Josjo2               | wimax2              | Josjo2-wimax2                 |

## Flow identifiers ##

We've seen that both code simulation and SimInfo files use _flow\_ids_ (flow identifiers). Those identifiers are numeric integers (beginning at 1, not 0) and its order is defined by the moment the flow starts.

So, if you have an application starting at 1 sec, another at 1.5 sec, and a third one at 2 sec, three flows with IDs 1, 2 and 3 will be created. Note that you should not start two different applications at the same time so there would be no way to make a correspondence between the apps and the flow identifiers.