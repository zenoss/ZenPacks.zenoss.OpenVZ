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

    container_status = None
    description = None
    hostname = None
    ipaddrs = []
    onboot = None
    ostemplate = None
    ve_root = None
    ve_private = None

    _properties = ManagedEntity._properties + (
        {'id': 'container_status', 'type': 'string', 'mode': 'w'},
        {'id': 'description', 'type': 'string', 'mode': 'w'},
        {'id': 'hostname', 'type': 'string', 'mode': 'w'},
        {'id': 'ipaddrs', 'type': 'lines', 'mode': 'w'},
        {'id': 'onboot', 'type': 'boolean', 'mode': 'w'},
        {'id': 'ostemplate', 'type': 'string', 'mode': 'w'},
        {'id': 've_root', 'type': 'string', 'mode': 'w'},
        {'id': 've_private', 'type': 'string', 'mode': 'w'},
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

    def getManagedDevice(self):
        if self.id == "0":
            return self.device()
        for ip in self.ipaddrs:

            # search "manageIp":
            # This first test will only search the primary IP that is used to monitor/model the device
            # which shows up in the top-left corner of the device's page:

            device = self.dmd.Devices.findDeviceByIdOrIp(ip)
            if device:
                return device
            
            # search additional IP addresses that may be associated with interfaces on a device:

            foundip = self.dmd.Networks.findIp(ip) 
            if foundip.device():
                return foundip.device()

        return None
        
