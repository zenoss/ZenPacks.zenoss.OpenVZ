##########################################################################
#
#   Copyright 2011 Zenoss, Inc. All Rights Reserved.
#
##########################################################################

# This modeler plugin can be tested on an OpenVZ host by running:
# zenmodel run -v10 --device="10.0.1.2"
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
    command = 'if [ ! -r /proc/user_beancounters ]; then echo "no"; else echo "yes"; %s; echo "#veinfo-stop"; for fn in /etc/vz/conf/[0-9]*.conf; do ( VEID="${fn##*/}"; VEID="${VEID%%.conf}"; source $fn; echo; echo $VEID; echo $NAME; echo $OSTEMPLATE; echo $DESCRIPTION; echo $VE_ROOT; echo $VE_PRIVATE; echo $ONBOOT); done; fi' % VZInfoParser.command

    def process(self, device, results, log):
        # call self.relMap() helper method that initializes relname and compname for me
        # 
        rm = self.relMap()
        lines = results.split('\n')
        if lines[0] != "yes":
            # we are not in a container or on a host
            return []   
        pos = 1 
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
            else:    
                if lines[pos+1]:
                    om.title = lines[pos+1]
                om.description = lines[pos+3]
                om.id = self.prepId(lines[pos])
                om.ostemplate = lines[pos+2]
                om.ve_root = lines[pos+4]
                om.ve_private = lines[pos+5]
                om.onboot = False
                if lines[pos] in vzinfo:
                        om.container_status = vzinfo[lines[pos]]
                if lines[pos+6] == "yes":
                        om.onboot = True
            pos += 8
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

        return rm
