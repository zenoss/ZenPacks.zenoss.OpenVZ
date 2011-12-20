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

    ostemplate = schema.TextLine(title=_t(u'OS Template'))
    ve_root = schema.TextLine(title=_t(u'VE Root Path'))
    ve_private = schema.TextLine(title=_t(u'VE Private Path'))
    onboot = schema.Bool(title=_t(u'Start On Boot'))
