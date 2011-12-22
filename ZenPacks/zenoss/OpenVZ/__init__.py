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

unused(Globals)

# Add relations to the base device class.
Device._relations += (('openvz_containers', ToManyCont(ToOne,
    'ZenPacks.zenoss.OpenVZ.Container.Container', 'host')), )

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
