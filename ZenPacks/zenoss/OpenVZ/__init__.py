##########################################################################
#
#   Copyright 2009, 2011 Zenoss, Inc. All Rights Reserved.
#
##########################################################################

import logging
log = logging.getLogger('zen.OpenVZ')

import Globals

from Products.ZenModel.Device import Device
from Products.ZenModel.DeviceHW import DeviceHW
from Products.ZenRelations.RelSchema import ToManyCont, ToOne
from Products.ZenModel.ZenPack import ZenPack as ZenPackBase
from Products.ZenUtils.Utils import unused, monkeypatch
from Products.Zuul.interfaces import ICatalogTool

unused(Globals)

# Add relations to the base device class. This is the best method for adding capabilities to an existing
# Linux system. 
Device._relations += (('openvz_containers', ToManyCont(ToOne,
    'ZenPacks.zenoss.OpenVZ.Container.Container', 'host')), )

# Add some new properties to device.hw, which we will use for recording the OS architecture as well as
# pagesize. Set defaults and add only if they don't already exist:

if not hasattr(DeviceHW, 'page_size'):
    DeviceHW.page_size = 4096
    DeviceHW._properties += ({ 'id' : 'pagesize', 'type': 'int', 'mode': 'w'},)

if not hasattr(DeviceHW, 'arch'):
    DeviceHW.arch = "x86_64"
    DeviceHW._properties += ({ 'id' : 'arch', 'type' : 'string', 'mode': 'w'},)

@monkeypatch("Products.ZenModel.Device.Device")
def getOpenVZComponentOnHost(self):
    # returns the component on the OpenVZ host, so we can link from an OpenVZ container
    # that is managed (SNMP/SSH) to the container component on the host.
    catalog = ICatalogTool(self.dmd)
    # for each Container ....
    for record in catalog.search('ZenPacks.zenoss.OpenVZ.Container.Container'):
        c = record.getObject()
        # for each IP address in the Container...
        for c_ip in c.ipaddrs:
            if c_ip == self.manageIp:
                return c
            # for each interface on our device:
            for iface in self.os.interfaces():
                # for each IP address on our interface:
                for our_ip in iface.getIpAddresses():
                    if c_ip == our_ip.split("/")[0]:
                        return c        
        for c_mac in c.macaddrs:
            for iface in self.os.interfaces():
                our_mac = iface.getInterfaceMacaddress().lower()
                if our_mac == c_mac:
                    return c
    return

# old-school monkeypatch
foo = Device.getExpandedLinks
def openvz_getExpandedLinks(self):
    links = foo(self)
    host = self.getOpenVZComponentOnHost()
    if host:
        links = '<a href="%s">OpenVZ Container %s on Host %s</a><br/>' % (host.getPrimaryUrlPath(), host.titleOrId(), host.device().titleOrId()) + links
    return links
Device.getExpandedLinks = openvz_getExpandedLinks
 
class ZenPack(ZenPackBase):
    def install(self, app):
        ZenPackBase.install(self, app)

        self.rebuildRelations(app.zport.dmd)

    def remove(self, app, leaveObjects=False):
        if not leaveObjects:
            Device._relations = tuple(
                [x for x in Device._relations if x[0] != 'openvz_containers'])

            self.rebuildRelations(app.zport.dmd)

        ZenPackBase.remove(self, app, leaveObjects=leaveObjects)

    def rebuildRelations(self, dmd):
        for d in dmd.Devices.getSubDevicesGen():
            d.buildRelations()
