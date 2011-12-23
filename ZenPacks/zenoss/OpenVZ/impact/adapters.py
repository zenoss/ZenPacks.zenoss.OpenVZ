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
        
        comp = self._object.getOpenVZComponentOnHost()
        if comp:

            # we are a device monitored thru SNMP or ssh that is an OpenVZ container. The
            # call above found the host we are running on, and the component representing
            # us underneath it. We are now going to say that we *are* the component, from
            # the container device's perspective. We depend on it, and it depends on us:

            yield ImpactEdge(
                IGlobalIdentifier(comp).getGUID(),
                IGlobalIdentifier(self._object.device()).getGUID(),
                self.relationship_provider 
            )

            yield ImpactEdge(
                IGlobalIdentifier(self._object.device()).getGUID(),
                IGlobalIdentifier(comp).getGUID(),
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

        # Try to find a device that exists because we are running net-snmp or have ssh monitoring
        # going direct to the container. If we find such a device, then this device *is* the container.
        # We, the container component, are dependent on this device. The device is dependent on us.
        # The code below yields both ImpactEdges from the container component's perspective.

        md = self._object.getManagedDevice()
        if md:
            yield ImpactEdge(
                IGlobalIdentifier(self._object.device()).getGUID(),
                IGlobalIdentifier(md).getGUID(),
                self.relationship_provider
            )
            yield ImpactEdge(
                IGlobalIdentifier(md).getGUID(),
                IGlobalIdentifier(self._object.device()).getGUID(),
                self.relationship_provider
            )

