odoo.define('wantech_treeview_selected_total.wantech_treeview_selected_total', function(require) {
    'use strict';
    var ListRenderer = require('web.ListRenderer');
    ListRenderer.include({
        groups: {},
        _onSelectRecord: function(event) {
            var self = this;
            var res = this._super(event);
            var $selectedRows = this.$('tbody .o_list_record_selector input:checked')
                .closest('tr');
            this.selection = _.map($selectedRows, function(row) {
                return $(row).data('id');
            });
            if (this.selection) {
                var gps = [];
                var els = this.$('.o_list_view_grouped > tbody > .o_group_header');
                var index = 0;
                _.forEach(self.groups, function(record) {
                    if (record.count > 0) {
                        record.aggValues = {};
                        for (var k in record.aggregateValues) {
                            record.aggValues[k] = 0;
                        }
                        _.forEach(record.data, function(d) {
                            _.forEach(self.selection, function(selection) {
                                if (d) {
                                    if (selection === d.id) {
                                        for (var k in record.aggregateValues) {
                                            record.aggValues[k] += d.data[k];
                                        }
                                    }
                                }
                            });
                        });
                    }
                    var c = 0;
                    var elems = self.$(els[index]).find('.o_list_number');
                    for (var key in record.aggValues) {
                        self.$(els[index]).find('.'+key).html(record.aggValues[key].toFixed(2));
                        if(self.$(els[index]).find('.'+key).length == 0){
                            $(elems[c++]).html(record.aggValues[key].toFixed(2));
                        }
                    }
                    index++;
                    gps.push(record);
                });
            }
            return this._super(event);
        },
        _renderGroups: function(data, groupLevel) {
            this.groups = data;
            return this._super(data, groupLevel);
        }
    });
});