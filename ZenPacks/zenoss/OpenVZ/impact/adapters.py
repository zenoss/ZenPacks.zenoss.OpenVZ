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
from ZenPacks.zenoss.Impact.stated.interfaces import IStateProvider

from ZenPacks.zenoss.OpenVZ.Container import Container

# To test, restart everything and then run:
# zenimpactgraph run --reset

# This will load new impact rules.


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

            e1 = IGlobalIdentifier(comp).getGUID()
            e2 = IGlobalIdentifier(self._object.device()).getGUID()

            yield ImpactEdge(e1, e2, self.relationship_provider)
            yield ImpactEdge(e2, e1, self.relationship_provider)


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
            e1 = IGlobalIdentifier(self._object.device()).getGUID()
            e2 = IGlobalIdentifier(md).getGUID()

            yield ImpactEdge(self.relationship_provider, e1, e2)
            yield ImpactEdge(self.relationship_provider, e2, e1)


# This following code is designed to set the the impact state of a container to down when
# the container is not running, thus causing any related services to be treated as down.

class ContainerStateProvider(object):
    implements(IStateProvider)

    def __init__(self, adapted):
        self._object = adapted

    @property
    def eventClasses(self):
        return ('/Status',)

    @property
    def excludeClasses(self):
        return None

    @property
    def eventHandlerType(self):
        return "WORST"

    @property
    def stateType(self):
        return 'AVAILABILITY'

    def calcState(self, events):
        if self._object.container_status == "running":
            return "UP", None
        else:
            return "DOWN", None
