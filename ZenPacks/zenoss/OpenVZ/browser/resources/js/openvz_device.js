/* This javascript is handed to the client's browser as-is, so any renderers or anything
else can be debugged in the browser using a JavaScript console or similar. */

(function(){

var ZC = Ext.ns('Zenoss.component');

ZC.registerName('OpenVZContainer', _t('OpenVZ Container'), _t('OpenVZ Containers'));

Ext.apply(Zenoss.render, {
    checkbox: function(bool) {
        if (bool) {
            return '<input type="checkbox" checked="true" disabled="true">';
        } else {
            return '<input type="checkbox" disabled="true">';
        }
    }
});

ZC.OpenVZContainerPanel = Ext.extend(ZC.ComponentGridPanel, {
    constructor: function(config) {
        config = Ext.applyIf(config||{}, {
            autoExpandColumn: 'description',
            componentType: 'OpenVZContainer',
            /* New capability in 4.x: set the default sort field and order: */
            sortInfo: {
                field: 'id',
                direction: 'ASC'
            },
            fields: [
                {name: 'uid'},
                {name: 'name'},
                {name: 'id'},
                {name: 'title'},
                {name: 'severity'},
                {name: 'container_status'},
                {name: 'managed_device'},
                {name: 'ostemplate'},
                {name: 'description'},
                {name: 'hostname'},
                {name: 'ipaddrs'},
                {name: 'onboot'},
                {name: 'monitor'},
                {name: 'monitored'},
                {name: 'locking'}
            ],
            columns: [{
                id: 'severity',
                dataIndex: 'severity',
                header: _t('Events'),
                renderer: Zenoss.render.severity,
                sortable: true,
                width: 50
            },{
                id: 'id',
                dataIndex: 'id',
                header: _t('VEID'),
                width: 40,
                sortable: true
            },{
                id: 'title',
                dataIndex: 'title',
                header: _t('Name'),
                sortable: true
            },{
                id: 'description',
                dataIndex: 'description',
                header: _t('Description'),
                sortable: true
            },{
                id: 'hostname',
                dataIndex: 'hostname',
                header: _t('Hostname'),
                sortable: true,
                width: 80
            },{
                id: 'ipaddrs',
                dataIndex: 'ipaddrs',
                header: _t('IP Addresses'),
                sortable: false,
                renderer: function(obj) {
                    if (obj)
                        return obj.join(" ");
                },
                width: 100
            },{
                id: 'managed_device',
                dataIndex: 'managed_device',
                header:_t('Device'),
                renderer: function(obj) {
                    if (obj && obj.uid && obj.name) {
                        return Zenoss.render.link(obj.uid, undefined, obj.name);
                    } else {
                        return "unmanaged";
                    }
                },
                width: 120
            },{
                id: 'ostemplate',
                dataIndex: 'ostemplate',
                header: _t('OS Template'),
                sortable: true,
                width: 120
            },{
                id: 'onboot',
                dataIndex: 'onboot',
                header: _t('On Boot'),
                renderer: Zenoss.render.checkbox,
                sortable: true,
                width: 60
            },{
                id: 'container_status',
                dataIndex: 'container_status',
                header:_t('Status'),
                width: 65
            },{
                id: 'monitored',
                dataIndex: 'monitored',
                header: _t('Monitored'),
                renderer: Zenoss.render.checkbox,
                sortable: true,
                width: 65
            },{
                id: 'locking',
                dataIndex: 'locking',
                header: _t('Locking'),
                renderer: Zenoss.render.locking_icons,
                width: 65
            }]
        });
        ZC.OpenVZContainerPanel.superclass.constructor.call(this, config);
    }
});

Ext.reg('OpenVZContainerPanel', ZC.OpenVZContainerPanel);

})();
