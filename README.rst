======================
ZenPacks.zenoss.OpenVZ
======================

.. contents::
    :depth: 3

This project is a Zenoss extension (ZenPack) that provides specialized
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

ChangeLog
---------

1.0.2 January 10, 2012
~~~~~~~~~~~~~~~~~~~~~~

* The `zenoss.cmd.linux.OpenVZ` modeler plugin will now automatically bind the
  `OpenVZHost` monitoring template to a device if a device is found to be an
  OpenVZ host. This eliminates a manual configuration step.

* The ZenPack installer will now automatically add the `zenoss.cmd.linux.OpenVZ`
  modeler plugin to the `/Server/Linux` and `/Server/SSH/Linux` device classes
  if they exist. This eliminates a manual configuration step.

1.0.1 January 9, 2012
~~~~~~~~~~~~~~~~~~~~~

* Initial code from Chet to auto-bind OpenVZHost Monitoring Template from the
  Modeling Plugin. Not yet working. Very close.

* Two new event transforms to force a remodel of the OpenVZ host when an
  ``openvz_container_created`` or ``openvz_container_destroyed`` event is fired.
  This will keep the OpenVZ Containers components list up-to-date within a
  few minutes.

* New Config Error Event when the host utilization command parser cannot
  retrieve all necessary metrics from ``/proc/user_beancounters`` to calculate
  OpenVZ Memory Utilization metrics.

* Removed left-over example code.

1.0.0 Release
~~~~~~~~~~~~~

Initial Release.

Requirements and Dependencies
-----------------------------

This ZenPack has been written to be compatible with Zenoss versions 3.2 through
4.1+. So far, it has only been tested up to Zenoss 4.1.1. If you experience
bugs, please file an issue at
https://github.com/zenoss/ZenPacks.zenoss.OpenVZ/issues.

Installation
------------

You must first have, or install, Zenoss 3.2.0 or later. Core and Enterprise
versions are supported. You can download the free Core version of Zenoss from
http://community.zenoss.org/community/download .

Normal Installation (packaged egg)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To install ZenPacks, there is only one daemon that needs to be running. For
Zenoss versions earlier than 4.0 this daemon is `zeoctl` for Zenoss 4.0 and
later this daemon is `zeneventserver`.

Best practice to install ZenPacks::

 $ zenoss stop
 $ zeneventserver start
 $ zenpack --install foo.egg
 $ zenoss start

For 3.x, use ``zeoctl`` instead of ``zeneventserver``.

Developer Installation (link mode)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you wish to further develop and possibly contribute back to this ZenPack
then you should clone the git repository and install the ZenPack in
developer mode using the following commands::

 git clone git://github.com/zenoss/ZenPacks.zenoss.OpenVZ.git
 zenpack --link --install ZenPacks.zenoss.OpenVZ
 zenoss restart

Usage
-----

To ensure the OpenVZ host system is being monitored, ensure that the
``zenoss.cmd.linux.OpenVZ`` modeler plugin is enabled for the host system.
Note that this will require Zenoss to be configured with ``root`` 
credentials to monitor the OpenVZ host via SSH, as all OpenVZ data is
extracted over SSH and ``root`` access is required to access this data.

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

Container Metrics and Graphs
----------------------------

.. Note:: These settings can be viewed by navigating to ``Advanced``, ``Monitoring
 Templates``, ``OpenVZContainer``, ``/Server`` in the UI.

By default, each Container component on an OpenVZ host has three graphs showing
number of processes, open files and memory utilization of each container. These
graphs are based on data extracted from ``/proc/user_beancounters`` on the
OpenVZ host.

This ZenPack has been written to allow you to monitor the full content of 
``/proc/user_beancounters``, but because of the large number of potential Data
Points, only a handful of Data Points have been enabled by default in order
to allow the default graphs to be displayed:

* ``numfile``
* ``numfile.maxheld``
* ``numproc``
* ``numproc.maxheld``
* ``oomguarbytes``
* ``oomguarbytes.maxheld``
* ``privvmbytes``
* ``privvmbytes.maxheld``

Additional Data Points can be added to the ``openvz`` datasource. All you need
to do is name the Data Point according to the naming convention described here,
and the OpenVZ ZenPack will populate the Data Point with RRD data.

The name of the Data Point should be of the following format:

* ``[resource]``
* ``[resource].maxheld``
* ``[resource].barrier``
* ``[resource].limit``
* ``[resource].failcnt``

Any resource name that is visible in ``/proc/user_beancounters`` can be used.
These Data Points should be created as type of GAUGE with the appropriate name.
The monitoring template will correlate the beancounter name with the metric
name and populate it with data.

.. Note:: OpenVZ allows individual resource limits to be disabled by setting
 the ``barrier`` and/or ``limit`` value to ``LONG_MAX`` (typically
 9223372036854775807 on 64-bit systems. The OpenVZ monitoring template will
 detect ``LONG_MAX`` when it is set and will *not* write this data out to
 RRD, as it indicates "Unlimited" rather than a valid numerical value. This
 will result in NaN data for "Unlimited" ``barrier`` and ``limit`` values.

In addition, the OpenVZ ZenPack implements a number of enhanced capabilities
regarding Data Points:

* For every data point ending in "pages", there is a
  corresponding Data Point ending in "bytes" that has been normalized from memory
  pages to bytes. This is used for the datapoint ``openvz.oomguarbytes`` to get a
  byte-normalized value of ``oomguarpages`` from ``/proc/user_beancounters``, for
  example.

* There is an additional ``.failrate`` suffix that can be created as a 
  DERIVED RRD Type with a minimum value of 0 and used for firing events when the
  value increments.

Host Metrics and Graphs
-----------------------

.. Note:: These settings can be viewed by navigating to ``Advanced``, ``Monitoring
 Templates``, ``OpenVZHost``, ``/Server`` in the UI.

OpenVZ hosts have two Data Sources: ``openvz`` and ``openvz_util``. ``openvz``
is used for collecting container status and firing events on container status
change. It is not intended to be changed at all. 

The ``openvz_util`` Data Source is used for monitoring host utilization and can
be modified by the user. It works similarly to the Container's ``openvz`` Data
Source in that a sampling of Data Points have been added by default, but more
can be added by the end user for metrics of interest. The Data Point names that
are recognized are:

* ``containers.[resource]``
* ``host.[resource]``
* ``utilization.ram``
* ``utilization.ramswap``
* ``utilization.allocated``

``containers.[resource]`` and ``host.[resource]`` Data Points can be created,
where ``[resource]`` is any resource name listed in
``/proc/user_beancounters``. Any resource name beginning with ``containers.``
will contain the total current value of that resource for all containers on the
system. For example, ``containers.oomguarpages`` will contain the sum of all
``oomguarpages`` for all containers on the host. The ``host.[resource]`` prefix
can be used to extract the current value of the corresponding resource for the
host, that is, VEID 0.

OpenVZ Container Memory Utilization Graph
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A very useful graph has been defined for the OpenVZ host, called "OpenVZ 
Container Memory Utilization." Using data from ``/proc/user_beancounters``,
a number of key metrics related to the memory utilization of all containers
on the host are calculated and presented in percentage form, based on the
formulas described here: http://wiki.openvz.org/UBC_systemwide_configuration

* RAM and Swap Allocated - how much RAM and Swap has been allocated (but may
  not yet be used). This value can exceed 1.0 (100% in the graph.)

* RAM and Swap Used - how much RAM and Swap has actually been used. Thresholds
  are defined for high values.

* RAM Used - how much RAM has been used. Values from 0.8 to 1.0 (80% to 100%
  in the graph) are acceptable.

This graph can be used to optimize the capacity of your OpenVZ hosts. In general,
you want to maximize memory utilization without hitting too high a value for "RAM
and Swap Used".

.. Note:: OpenVZ also has commitment level formulas. These have not yet been
 integrated into the OpenVZ ZenPack at this time, but will be in the future. For
 commitment levels to work correctly, all containers on the host must have
 active memory resource limits. However, the metrics described above are available
 for all OpenVZ hosts, whether memory resource limits are active or not.

TODO
----

Future plans for development of this ZenPack include:

* OpenVZ Host: Integrate Commitment Level Formulas
* OpenVZ Containers: collect ``/proc/vz/vestat`` (uptime and load data) for each container
* OpenVZ Host: provide cumulative ``failcnt`` and ``failrate`` Data Points for host-wide failcnt eventing
* Container detection could be a bit more sophisticated. a stray ``vzctl`` command with a non-existent VEID
  will create a config file, yet it does not exist, and vzlist does not display it. Yet we list it.
* Add tests!

To submit new feature requests, bug reports, and submit improvements, visit the
OpenVZ ZenPack on GitHub:

https://github.com/zenoss/ZenPacks.zenoss.OpenVZ
