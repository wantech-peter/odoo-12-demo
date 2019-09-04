odoo.define('wantech_reordering_divide_multiply.wantech_reordering_divide_multiply', function(require) {
    "use strict";

    var core = require('web.core');
    var BaseImport = require('base_import.import');
    var ListController = require('web.ListController');
    var QWeb = core.qweb;
    var _t = core._t;
    var rpc = require('web.rpc');
    var weContext = require('web_editor.context');
    var Dialog = require('web.Dialog');

    ListController.include({
        context: {},
        renderButtons: function($node) {
            var self = this;
            this._super.apply(this, arguments);
            if (!this.noLeaf && this.hasButtons) {
                this.$buttons.on('click', '.reod_prod_qty_updt_mul', this.reod_prod_qty_updt_mul.bind(this));
                this.$buttons.on('click', '.reod_prod_qty_updt_div', this.reod_prod_qty_updt_div.bind(this));
            }
        },
        reod_prod_qty_updt_div: function() {
            var val = $('.o_input_quant_multiple').val();
            var self = this;
            console.log(val, isNaN(val));
            if(isNaN(val) || val === '')
            {
                var $content = $('<p/>').text(_t('The values for the multiplier can only be Integers.'));
                        var dialog = new Dialog(self, {
                            title: _t('Error'),
                            $content: $content,
                        });
                        dialog.open();
                return;
            }
            rpc.query({
                    model: 'stock.warehouse.orderpoint',
                    method: 'quantity_update',
                    args: [{
                        value: val,
                        operator: "/"
                    }]
                })
                .then(function(result) {
                    if (result) {
                        window.location.reload();
                    } else {
                        var $content = $('<p/>').text(_t('Some error occured, please check if you\'re connected to a network.'));
                        var dialog = new Dialog(self, {
                            title: _t('Error'),
                            $content: $content,
                        });
                        dialog.open();
                    }
                });
        },
        reod_prod_qty_updt_mul: function() {
            var val = $('.o_input_quant_multiple').val();
            var self = this;
            console.log(val,isNaN(val));
            if(isNaN(val) || val === '')
            {
                var $content = $('<p/>').text(_t('The values for the multiplier can only be Integers.'));
                        var dialog = new Dialog(self, {
                            title: _t('Error'),
                            $content: $content,
                        });
                        dialog.open();
                return;
            }
            rpc.query({
                    model: 'stock.warehouse.orderpoint',
                    method: 'quantity_update',
                    args: [{
                        value: val,
                        operator: "*"
                    }]
                })
                .then(function(result) {
                    if (result) {
                        window.location.reload();
                    } else {
                        var $content = $('<p/>').text(_t('Some error occured, please check if you\'re connected to a network.'));
                        var dialog = new Dialog(self, {
                            title: _t('Error'),
                            $content: $content,
                        });
                        dialog.open();
                    }
                });
        },
    });
});