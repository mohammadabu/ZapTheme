odoo.define('theme_zap.for_testing', function (require) {
    'use strict';
    var core = require('web.core');
    var wUtils = require('website.utils');
    var publicWidget = require('web.public.widget');
    var _t = core._t;
    publicWidget.registry.for_testing = publicWidget.Widget.extend({
        selector: '.for_testing',
        disabledInEditableMode: false,
        start: function () {
            console.log('yeeeeeees')
        }
    })

})
    