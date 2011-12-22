##########################################################################
#
#   Copyright 2009, 2011 Zenoss, Inc. All Rights Reserved.
#
##########################################################################

import logging
log = logging.getLogger('zen.OpenVZ')

import Globals

from Products.ZenModel.Device import Device
from Products.ZenRelations.RelSchema import ToManyCont, ToOne
from Products.ZenModel.ZenPack import ZenPack as ZenPackBase
from Products.ZenUtils.Utils import unused, monkeypatch
from Products.Zuul.interfaces import ICatalogTool

unused(Globals)

# Add relations to the base device class.
Device._relations += (('openvz_containers', ToManyCont(ToOne,
    'ZenPacks.zenoss.OpenVZ.Container.Container', 'host')), )

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
