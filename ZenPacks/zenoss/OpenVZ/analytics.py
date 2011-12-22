######################################################################
#
# Copyright 2011 Zenoss, Inc.  All Rights Reserved.
#
######################################################################

from zope.component import adapts
from zope.interface import implements

from Products.Zuul.interfaces import IReportable

from ZenPacks.zenoss.ZenETL.reportable \
    import Reportable, MARKER_LENGTH, DEFAULT_STRING_LENGTH

from ZenPacks.zenoss.OpenVZ.Container import Container


class BaseReportable(Reportable):
    implements(IReportable)

    def __init__(self, context):
        self.context = context

class ContainerReportable(BaseReportable):
    adapts(Container)

    @property
    def entity_class_name(self):
        return 'openvz_container'

    def reportProperties(self):
        return [
            ('id', 'string', self.context.id, DEFAULT_STRING_LENGTH),
            ('name', 'string', self.context.title, DEFAULT_STRING_LENGTH),
            ('ostemplate', 'string', self.context.ostemplate, DEFAULT_STRING_LENGTH)
        ]
