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

    # PersistentList()
    # PersistentDict()
    #
    # The attributes below are stored by Zope. If you are storing a simple
    # type like an int or string, Zope will be able to tell when its value is
    # updated. Also, if you use a list or a dict, and the list or dict itself
    # is re-created each time it is updated, Zope will be able to tell that
    # the list or dict is updated.
    #
    # However, if you are changing, adding or removing elements from an existing
    # list, or adding, removing or updating dictionary key/value pairs, Zope will
    # not be able to tell that the updates have happened. There are two ways
    # to deal with this. The first is to explicitly call _p_changed on your Component
    # once you have made any changes that need to persist:
    # 
    # myContainer._p_changed = True
    # 
    # The other method is to use PersistentList() and PersistentDict() as your
    # list and dict objects when you create them, which will allow Zope to detect
    # that they have been changed and persist the changes in the ZODB.

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
        
