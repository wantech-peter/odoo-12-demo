//odoo.define('exist_sale_order.register', function (require) {
//"use strict";
//    console.log("gggggggggggggggggggggggggggg")
//    var ajax = require('web.ajax');
//    var core = require('web.core');
//    var Dialog = require('web.Dialog');
////    var crash_manager = require('web.RedirectWarningHandler');
//    console.log("gggggggggggggggggggggggggggg",Dialog)
//
//    var QWeb = core.qweb;
//    var _t = core._t;
//    var _lt = core._lt;
//
//var MyRedirectWarningHandler = crash_manager.ExceptionHandler.extend({
//    init: function(parent, error) {
//
//        this._super(parent);
//        this.error = error;
//    },
//    display: function() {
//        var self = this;
//        var error = this.error;
//        error.data.message = error.data.arguments[0];
//
//        new Dialog(this, {
//            size: 'medium',
//            title: _.str.capitalize(error.type) || _t("Odoo Warning"),
//            buttons: [
//                {text: error.data.arguments[3], classes : "btn-primary", click: function() {
//
//                    window.location.href = '#action='+error.data.arguments[1];
//                    window.location.href = '#id='+error.data.arguments[2]+'&action='+error.data.arguments[1];
//
//
//                    self.destroy();
//                }},
//                {text: _t("Cancel"), click: function() { self.destroy(); }, close: true}
//            ],
//            $content: QWeb.render('CrashManager.warning', {error: error}),
//        }).open();
//    }
//});
//core.crash_registry.add('odoo.addons.exist_sale_order.exception.MyRedirectWarning', MyRedirectWarningHandler);
//});
