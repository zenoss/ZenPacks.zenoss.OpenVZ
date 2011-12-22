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
    ostemplate = ProxyProperty('ostemplate')
    description = ProxyProperty('description')
    ve_root = ProxyProperty('ve_root')
    ve_private = ProxyProperty('ve_private')
    onboot = ProxyProperty('onboot')
