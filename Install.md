# Introduction #

This tutorial shows how to create and simulate the performance of a wireless WAN (containing WiFi and/or WiMAX networks) integrating two powerful applications: [Radio Mobile](http://www.cplus.org/rmw/english1.html) (radio-systems simulator) and [ns-3](http://www.nsnam.org/) (discrete-event network simulator).

The goal of this project is twofold:

  * Provide code to interface Radio Mobile and ns-3.
  * Document the complete process of creation and simulation of networks.

You will need a Unix-like operating system (a Debian/Ubuntu distribution will be assumed for this tutorial).

## Radio Mobile ##

Radio Mobile is a freeware tool for plotting RF patterns and predicting the performance of radio systems. It's able to draw maps using terrain elevation data (SRTM, DTED, BIL, or GTOPO30) for automatic extraction of path profile between an emitter and a receiver. This data is added to system, environmental and statistical parameters to feed the [Irregular Terrain Model](http://en.wikipedia.org/wiki/Longley%E2%80%93Rice_model) radio propagation model.

Radio Mobile has some drawbacks though: firstly, it's not [free software](http://www.gnu.org/philosophy/free-sw.html) but freeware, and the source code is not available. Secondly, it's written in Visual Basic, so it's not multi-platform. Fortunately it runs in [Wine](http://www.winehq.org/), so you don't need to dual-boot or use a virtual machine.

If you are experienced with the software, check this thorough [Pizon tutorial](http://www.pizon.org/radio-mobile-tutorial/index.html).

## ns-3 ##

[ns-3](http://www.nsnam.org/) is a discrete-event network simulator for Internet systems. ns-3 is free software (GNU GPLv2 license) and is intended as an eventual replacement for the popular [ns-2](http://www.isi.edu/nsnam/ns/) simulator.

ns-3 is written in C++ even though it's possible to write simulations also with Python. Take a look at the [Tutorials](http://www.nsnam.org/tutorials.html) on how to use the simulator.

# Installation #

## Radio Mobile ##

  * Firstly, install _wine_:

```
$ apt-get install wine
```

  * Then download and install Radio Mobile following these [instructions](http://wireless.ictp.it/school_2005/download/radiomobile/index.html).

  * Elevation data: you can either download SRTM files ([mirror](http://dds.cr.usgs.gov/srtm/version1/)) to your local storage disk or, if you are in a high-speed network, let Radio Mobile download them when needed.

  * Finally, check that it works:

```
$ cd path/to/radiomobile/
$ wine rmweng.exe
```

## ns-3 ##

  * ns-3 uses _mercurial_ (command _hg_) as [SCM](http://en.wikipedia.org/wiki/Revision_control), so we need to install the package:

```
$ apt-get install mercurial
```

  * Download the _ns-3-allinone_ scripts from the [ns-3 code repository](http://code.nsnam.org):

```
$ hg clone http://code.nsnam.org/ns-3-allinone/
```

  * Run the script the download script. Make sure that _pybindgen_ is successfully installed.

```
$ cd ns-3-allinone
$ python download.py
```

  * Apply _wwplan_ patches: For now, this step is only compulsory if you plan to use QoS (that's it, tag packets with access classes AC\_xyz) with the OnOff application (more on this on [Simulate](Simulate.md)). Note that you must clone _wwplan_ source first (see next section).

```
$ patch -p1 < wwplan/patches/ns-3-dev-DATE.path
```

  * Compile (make sure that Python bindings are enabled in the _configure_ step):

```
$ cd ns-3-dev
$ ./waf configure 
$ ./waf build
```

## wwplan scripts ##

  * Install _python-yaml_:

```
$ apt-get install python-yaml
```

  * Checkout _wwplan_ sources to the ns-3 root directory:

```
$ cd ns-3-dev
$ hg clone http://wwplan.googlecode.com/hg/ wwplan 
```