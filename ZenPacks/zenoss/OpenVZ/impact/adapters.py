######################################################################
#
# Copyright 2011 Zenoss, Inc.  All Rights Reserved.
#
######################################################################

from zope.interface import implements
from zope.component import adapts

from Products.ZenModel.Device import Device
from Products.ZenUtils.guid.interfaces import IGlobalIdentifier

from ZenPacks.zenoss.Impact.impactd.interfaces import IRelationshipDataProvider
from ZenPacks.zenoss.Impact.impactd.relations import ImpactEdge

from ZenPacks.zenoss.OpenVZ.Container import Container

class BaseRelationsProvider(object):
    relationship_provider = "OpenVZ"

    def __init__(self, adapted):
        self._object = adapted

    def belongsInImpactGraph(self):
        return True

class DeviceRelationsProvider(BaseRelationsProvider):
    implements(IRelationshipDataProvider)
    adapts(Device)

    def getEdges(self):

        # We are saying below, that from the device's perspective, each container
        # depends upon us.

        devguid = IGlobalIdentifier(self._object).getGUID()
        for ve in self._object.openvz_containers():

            # For ImpactEdges, the second argument depends upon the first argument:

            yield ImpactEdge(
                devguid,
                IGlobalIdentifier(ve).getGUID(),
                self.relationship_provider
            )

class ContainerRelationsProvider(BaseRelationsProvider):
    implements(IRelationshipDataProvider)
    adapts(Container)

    def getEdges(self):

        # We are saying below that from the container's perspective, we depend
        # on the physical node. We are agreeing with the ImpactEdge defined in
        # DeviceRelationsProvider, just expressing this identical relationship
        # from the Container's perspective. When defining ImpactEdges, you
        # always want to define impact relationships from both sides like this. 

        yield ImpactEdge(
            IGlobalIdentifier(self._object.device()).getGUID(),
            IGlobalIdentifier(self._object).getGUID(),
            self.relationship_provider
        )
