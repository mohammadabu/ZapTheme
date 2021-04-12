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
            var self = this;
            var template = self.$target.data('template') || 'theme_zap.custom_snippet_template';
            console.log('yeeeeeees')
            console.log(self.$target)
            var prom = new Promise(function (resolve) {
                self._rpc({
                    route: '/blog/render_latest_posts',
                    params: {
                        template: template,
                        domain: [],
                        // limit: limit,
                    },
                }).then(function (posts) {
                    console.log(posts)
                }).guardedCatch(function () {
                    if (self.editableMode) {
                        self.$target.append($('<p/>', {
                            class: 'text-danger',
                            text: _t("An error occured with this latest posts block. If the problem persists, please consider deleting it and adding a new one"),
                        }));
                    }
                    resolve();
                });
            });
            return Promise.all([this._super.apply(this, arguments), prom]);
        }
    })

})
    