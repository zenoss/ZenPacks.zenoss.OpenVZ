
(function(){

var ZC = Ext.ns('Zenoss.component');

ZC.registerName('OpenVZContainer', _t('OpenVZ Container'), _t('OpenVZ Containers'));

Ext.apply(Zenoss.render, {
    entityLinkFromGrid: function(obj) { 
        if (obj && obj.uid && obj.title) {
            if ( !this.panel || this.panel.subComponentGridPanel) {
                return String.format(
                 '<a href="javascript:Ext.getCmp(\'component_card\').componentgrid.jumpToEntity(\'{0}\', \'{1}\');">{1}</a>',
                  obj.uid, obj.title);
            } else {
                return obj.title;
            }
        }
    },

    checkbox: function(bool) {
        if (bool) {
            return '<input type="checkbox" checked="true" disabled="true">';
        } else {
            return '<input type="checkbox" disabled="true">';
        }
    }
});

ZC.OpenVZStackComponentGridPanel = Ext.extend(ZC.ComponentGridPanel, {
    subComponentGridPanel: false,
    
    jumpToEntity: function(uid, name) {
        var tree = Ext.getCmp('deviceDetailNav').treepanel,
            sm = tree.getSelectionModel(),
            compsNode = tree.getRootNode().findChildBy(function(n){
                return n.text=='Components';
            });
    
        var compType = Zenoss.types.type(uid);
        var componentCard = Ext.getCmp('component_card');
        componentCard.setContext(compsNode.id, compType);
        componentCard.selectByToken(uid);
        sm.suspendEvents();
        compsNode.findChildBy(function(n){return n.id==compType;}).select();
        sm.resumeEvents();
    }
});

ZC.ContainerGridPanel = Ext.extend(ZC.OpenVZStackComponentGridPanel, {
    
    constructor: function(config) {
        config = Ext.applyIf(config||{}, {
            autoExpandColumn: 'title',
            componentType: 'OpenVZContainer',
            fields: [
                {name: 'uid'},
                {name: 'id'},
                {name: 'title'},
                {name: 'severity'},
		{name: 'guest_device'},
		{name: 'ostemplate'},
		{name: 've_root'},
		{name: 've_private'},
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
                id: 'guest_device',
                dataIndex: 'guest_device',
                header:_t('Guest Device'),
                renderer: function(obj) {
                    if (obj && obj.uid && obj.name) {
                        return Zenoss.render.link(obj.uid, undefined, obj.name);
                    }
                }
            },{
                id: 'ostemplate',
                dataIndex: 'ostemplate',
                header: _t('OS Template'),
                sortable: true,
                width: 65
            },{
                id: 've_root',
                dataIndex: 've_root',
                header: _t('VE Root'),
                sortable: true,
                width: 100
            },{
                id: 've_private',
                dataIndex: 've_private',
                header: _t('VE Private'),
                sortable: true,
                width: 100 
            },{
                id: 'onboot',
                dataIndex: 'onboot',
                header: _t('On Boot'),
                renderer: Zenoss.render.checkbox,
                sortable: true,
                width: 40 
            },{
                id: 'monitored',
                dataIndex: 'monitored',
                header: _t('Monitored'),
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
        ZC.OpenVZStackComponentGridPanel.superclass.constructor.call(this, config);
    }
});

Ext.reg('OpenVZContainerPanel', ZC.ContainerGridPanel);

})();
