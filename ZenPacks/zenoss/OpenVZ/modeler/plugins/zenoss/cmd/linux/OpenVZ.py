##########################################################################
#
#   Copyright 2011 Zenoss, Inc. All Rights Reserved.
#
##########################################################################

# This modeler plugin can be tested on an OpenVZ host by running:
# zenmodeler run -v10 --device="10.0.1.2"
#
# This modeler plugin is also imported by zenhub, so you should check zenhub.log for any tracebacks if your
# modeler plugin does not appear to be working.

from Products.DataCollector.plugins.CollectorPlugin import CommandPlugin
from Products.DataCollector.plugins.DataMaps import ObjectMap
from ZenPacks.zenoss.OpenVZ.util import VZInfoParser  

class OpenVZ(CommandPlugin):
    
    # These values tell zenhub how to check and potentially update our object heirarchy to reflect new changes to
    # devices. We define various values that zenhub uses to look at the right place in the object heirarchy, create
    # the right kinds of objects, and connect to the right relationships in our objects. These values are akin
    # to an "address" on an envelope that allows zenhub to get the relMap/objectMaps we return to the right location.

    # The values up here are static values that are used by helper functions self.relMap() and self.objectMap(), to
    # set corresponding internal values in the objects returned. We can also import relMap and objectMap and manually
    # create these objects ourselves, and set relname, modname, compname, classname ourselves, and this is often
    # required in more advanced scenarios.

    # relname is a relationship name, which is the same as the relationship name in the model class:
    relname = "openvz_containers"
    # this is the class we will instantiate... and it needs to match the container
    modname = "ZenPacks.zenoss.OpenVZ.Container"
    # we could also set compname up here if we wanted....
    # compname is used to hang things off of "os/" instead of off the device directly...
    # compname is anything we want to insert after our device but before our relationship, and can contain slashes....
    # the heirarchy of device/os/foo/bar MUST already exist and be created somewhere else.
    # device/os/interfaces/eth0
    #        ^^ ^^^^^^^^^^   ^^ 
    # device/os/interfaces/eth0/ips/foo
    #        ^^^^^^^^^^^^^^^^^^ ^^^ ^^^
    # above, first set of ^ is compname, second set is relname, third set is ID. See how compname changes length, relname
    # is always the last part before the ID........
    # classname will be set to "ZenPacks.zenoss.OpenVZ.Container.Container", auto-calculated based on modname (dup last name)
    command = 'if [ ! -r /proc/user_beancounters ]; then echo "no"; else echo "yes"; p="$(which python)"; [ -z "$py" ] && echo 4096 || $py -c "import resource; print(resource.getpagesize())"; /usr/bin/env uname -m; %s; echo "#veinfo-stop"; unset NAME HOSTNAME OSTEMPLATE IP_ADDRESS NETIF DESCRIPTION VE_ROOT VE_PRIVATE ONBOOT; for fn in /etc/vz/conf/[0-9]*.conf; do ( VEID="${fn##*/}"; VEID="${VEID%%.conf}"; source $fn; echo; echo $VEID; echo $NAME; echo $HOSTNAME; echo $OSTEMPLATE; echo $IP_ADDRESS; echo $NETIF; echo $DESCRIPTION; echo $VE_ROOT; echo $VE_PRIVATE; echo $ONBOOT); done; fi' % VZInfoParser.command

#   imported and called from zenhub... and have access to the model
#   def condition()

#   This method is imported and run by zenmodeler... and do not have access to the model

    def process(self, device, results, log):
        # call self.relMap() helper method that initializes relname and compname for me
        # 
        rm = self.relMap()
        lines = results.split('\n')
        if lines[0] != "yes":
            # we are not in a container or on a host
            return []   
        pos = 1
        try:
            page_size = int(lines[pos])
        except ValueError:
            page_size = 4096
        pos += 1
        arch = lines[pos]
        pos += 1
        hw_map = ObjectMap({"page_size" : page_size, "arch" : arch }, compname="hw")
        infolines = []
        while lines[pos] != "#veinfo-stop":
                infolines.append(lines[pos])
                pos += 1
        vzinfo = VZInfoParser.parse(infolines)
        # if we find VE 0, we are on a host...
        foundZero = False
        # blank line:
        pos += 2
        while pos < len(lines):
            # helper method - will set compname, modname, and classname for me:
            # it gets these settings from relname, modname, and classname = modname
            om = self.objectMap() 
            if lines[pos] == "0":
                foundZero = True
                om.title = "CT0"
                om.id = "0"
                om.description = "Hardware Node"
                om.onboot = False
                om.ve_root = "N/A"
                om.ve_private = "N/A"
                om.container_status = "running"
                om.ostemplate = "N/A"
                om.ipaddrs=[]
                om.macaddrs=[]
            else:    
                om.id = self.prepId(lines[pos])
                # NAME
                if lines[pos+1]:
                    om.title = lines[pos+1]
                om.hostname = lines[pos+2]
                om.ostemplate = lines[pos+3]
                # veth macaddr info on lines[pos+5]
                om.description = lines[pos+6]
                om.ve_root = lines[pos+7]
                om.ve_private = lines[pos+8]
                om.onboot = False
                if lines[pos] in vzinfo:
                    om.container_status = vzinfo[lines[pos]]
                    if om.container_status == "running":
                        om.ipaddrs = []
                        # only update IPs if running so the IPs stick around if the container is stopped during remodel,
                        # so we still have IPs for container component <-> managed device correlation :)
                        for ip in lines[pos+4].split():
                            om.ipaddrs.append(ip)
                        # again, only update MAC addresses from veth when we are in a running state, so we cache old
                        # ones for correlation if a container happens to be stopped...
                        om.macaddrs = []
                        for netif in lines[pos+5].split(";"):
                            keypairs = netif.split(",")
                            for kp in keypairs:
                                kv = kp.split("=")
                                if len(kv) != 2:
                                    continue
                                if kv[0] == "mac":
                                    om.macaddrs.append(kv[1].lower())
                if lines[pos+9] == "yes":
                    om.onboot = True
            pos += 11 
            rm.append(om)
        if not foundZero:
            return []
    # a relMap() is just a container to store objectMaps
    # in relmap and objectmap, there is a compname and modname
    # any 
    #
    #
    # objectmaps and relmaps are temporary objects that the modeler plugin sends to zenhub, which then determines
    # if the model needs to be updated. 
    # device/containers/106
    # om ^    relmap ^   om^
    # we are allowd to return:
        # a relmap - will be filled with object maps that are related to "device"
        # an objectmap - 
        # a list of relmaps, objectmaps

        # If we get here, we've identified this as an OpenVZ host. Create a new
        # ObjectMap that will be applied to the device. Use it to call our
        # setOpenVZHostTemplate method on the device to bind the host-level
        # monitoring template.
        device_map = ObjectMap()
        device_map.setOpenVZHostTemplate = True

        return [device_map, hw_map, rm]
