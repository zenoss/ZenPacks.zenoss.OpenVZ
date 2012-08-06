######################################################################
#
# Copyright 2011 Zenoss, Inc.  All Rights Reserved.
#
######################################################################

from zope.interface import implements

from Products.Zuul.decorators import info
from Products.Zuul.infos import ProxyProperty
from Products.Zuul.infos.component import ComponentInfo

from ZenPacks.zenoss.OpenVZ.interfaces import IContainerInfo


class BaseComponentInfo(ComponentInfo):
    title = ProxyProperty('title')

    @property
    def entity(self):
        return {
            'uid': self._object.getPrimaryUrlPath(),
            'title': self._object.titleOrId(),
        }

    @property
    def icon(self):
        return self._object.getIconPath()


class ContainerInfo(BaseComponentInfo):
    implements(IContainerInfo)

    container_status = ProxyProperty('container_status')
    description = ProxyProperty('description')
    hostname = ProxyProperty('hostname')
    ipaddrs = ProxyProperty('ipaddrs')

    # put @property first, then @info...
    @property
    @info
    def managed_device(self):
        return self._object.getManagedDevice()

    onboot = ProxyProperty('onboot')
    ostemplate = ProxyProperty('ostemplate')
    ve_root = ProxyProperty('ve_root')
    ve_private = ProxyProperty('ve_private')
