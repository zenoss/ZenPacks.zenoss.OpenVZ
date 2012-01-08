======================
ZenPacks.zenoss.OpenVZ
======================

.. contents::
    :depth: 3

This project is a Zenoss_ extension (ZenPack) that provides specialized
modeling and monitoring capabilities for `OpenVZ` hosts.

While Zenoss always has had the ability to monitor an OpenVZ host system and
containers (also called "VE"s) as standalone devices by connecting to the host
and containers directly using SSH or SNMP, it did not have the ability to
understand the relationship between the OpenVZ host and the container. It also
did not have the ability to "see" containers by simply monitoring the host.

This ZenPack allows you to see the containers as components within an OpenVZ
host even if you are not actively monitoring the individual containers. A
number of metrics are made available for the containers without requiring
monitoring to be configured on the containers themselves. This is a great
benefit for hosting providers as well as large enterprise OpenVZ deployments.

With this ZenPack, it is also still possible to monitor containers "the
old-fashioned way", as Linux devices by using SSH or SNMP, and if you do this,
Zenoss will now be able to "connect" the OpenVZ host to the container device
that you are monitoring. For containers containing production workloads,
this dual-monitoring approach allows you to use traditional Zenoss monitoring
and alerting functions within the container.

Requirements and Dependencies
-----------------------------

This ZenPack has been written to be compatible with Zenoss versions 3.2
through 4.2+. So far, it has only been tested on Zenoss 4.1.2. If you 
experience bugs with Zenoss 3.2, please file an issue against the package
at https://github.com/zenoss/ZenPacks.zenoss.OpenVZ/issues . 

Installation
------------

You must first have, or install, Zenoss 3.2.0 or later. Core and 
Enterprise versions are supported. You can download the free Core version
of Zenoss from http://community.zenoss.org/community/download .

Normal Installation (packaged egg)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To install ZenPacks, there is only one daemon that needs to be running:
``zeneventserver``.

Best practice to install ZenPacks::

 $ zenoss stop
 $ zeneventserver start
 $ zenpack --install foo.egg
 $ zenoss start

For 3.x, use ``zeoctl`` instead of ``zeneventserver``.

Developer Installation (link mode)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you wish to further develop and possibly contribute back to this ZenPack
then you should clone the git repository and install the ZenPack in
developer mode using the following commands::

 git clone git://github.com/zenoss/ZenPacks.zenoss.OpenVZ.git
 zenpack --link --install ZenPacks.zenoss.OpenVZ
 zenoss restart

Usage
-----

To ensure the OpenVZ host system is being monitored, ensure that the
``zenoss.cmd.linux.OpenVZ`` Modeler Plugin is enabled for the host system.
Note that this will require Zenoss to be configured with the proper
credentials to monitor the OpenVZ host via SSH, as all OpenVZ data is
extracted over SSH rather than SNMP.

With the modeler plugin enabled, remodeling the device should cause OpenVZ
Containers to be displayed as Components of the modeled device.  You should
also see relevant information for each container on the system, such as its
VEID, name, hostname, IP Address(es) (if assigned via venet), a link to the
device (if you are monitoring the container directly via SSH or SNMP), the OS
Template that was used to create the VE, the status of the "On Boot" flag and
its status (running, stopped, etc.)

To enable advanced functionality, it is recommended that you bind the
``/Server/OpenVZHost`` monitoring template to the OpenVZ host as well.  This
can be done by selecting ``Bind Templates`` under the Gear menu for the
device. When this is done, you will be able to receive Events when containers
are created, destroyed, started and stopped, and you will also be able to see
a global ``OpenVZ Container Memory Utilization`` graph on the device (under
Graphs for the host Device) which will allow you to actively monitor the
memory utilization of the containers and thus optimize the capacity of your
OpenVZ deployment.


