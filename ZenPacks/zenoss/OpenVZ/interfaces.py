######################################################################
#
# Copyright 2011 Zenoss, Inc.  All Rights Reserved.
#
######################################################################

from Products.Zuul.form import schema
from Products.Zuul.infos.component import IComponentInfo
from Products.Zuul.utils import ZuulMessageFactory as _t

class IContainerInfo(IComponentInfo):
    """Info adapter for OpenVZ Container components."""
    container_status = schema.TextLine(title=_t(u'Container Status'))
    description = schema.TextLine(title=_t(u'Description'))
    hostname = schema.TextLine(title=_t(u'Hostname'))
    ipaddrs = schema.List(title=_t(u'IP Addresses'))
    managed_device = schema.Entity(title=_t(u'Device'))
    onboot = schema.Bool(title=_t(u'Start On Boot'))
    ostemplate = schema.TextLine(title=_t(u'OS Template'))
    ve_root = schema.TextLine(title=_t(u'VE Root Path'))
    ve_private = schema.TextLine(title=_t(u'VE Private Path'))
