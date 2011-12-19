##########################################################################
#
#   Copyright 2011 Zenoss, Inc. All Rights Reserved.
#
##########################################################################

from Products.DataCollector.plugins.CollectorPlugin import CommandPlugin

class OpenVZ(CommandPlugin):
    relname = "openvz_containers"
    modname = "ZenPacks.zenoss.OpenVZ.Container"
    command = 'for fn in /etc/vz/conf/[0-9]*.conf; do ( VEID="${fn##*/}"; VEID="${VEID%.conf}"; source $fn; echo; echo $VEID; echo $NAME; echo $OSTEMPLATE; echo $VE_ROOT; echo $VE_PRIVATE; echo $ONBOOT); done'

    def process(self, device, results, log):
        rm = self.relMap()
        lines = results.split('\n')
        pos = 1
        while pos < len(lines):
            om = self.objectMap() 
            om.id = self.prepId(lines[pos])
            if lines[pos+1]:
                    om.title = lines[pos+1]
            om.ostemplate = lines[pos+2]
            om.ve_root = lines[pos+3]
            om.ve_private = lines[pos+4]
            om.onboot = False
            if lines[pos+5] == "yes":
                om.onboot = True
            pos += 7
            rm.append(om)
	return rm
