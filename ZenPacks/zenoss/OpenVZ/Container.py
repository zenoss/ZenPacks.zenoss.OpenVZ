##########################################################################
#
#   Copyright 2009, 2011 Zenoss, Inc. All Rights Reserved.
#
##########################################################################

from Products.ZenModel.DeviceComponent import DeviceComponent
from Products.ZenModel.ManagedEntity import ManagedEntity
from Products.ZenRelations.RelSchema import ToOne, ToManyCont
from Products.ZenModel.ZenossSecurity import ZEN_CHANGE_DEVICE


class Container(DeviceComponent, ManagedEntity):
    meta_type = portal_type = "OpenVZContainer"

    ostemplate = None
    ve_root = None
    ve_private = None
    onboot = None

    _properties = ManagedEntity._properties + (
        {'id': 'ostemplate', 'type': 'string', 'mode': 'w'},
        {'id': 've_root', 'type': 'string', 'mode': 'w'},
        {'id': 've_private', 'type': 'string', 'mode': 'w'},
        {'id': 'onboot', 'type': 'boolean', 'mode': 'w'},
        )

    _relations = ManagedEntity._relations + (
        ('host', ToOne(ToManyCont,
            'Products.ZenModel.Device.Device',
            'openvz_containers')
            ),
        )

    # This makes the "Graphs" and "Templates" component displays available.
    factory_type_information = ({
        'actions': ({
            'id': 'perfConf',
            'name': 'Template',
            'action': 'objTemplates',
            'permissions': (ZEN_CHANGE_DEVICE,),
            },),
        },)

    def name(self):
        return self.id

    def device(self):
        return self.host()
