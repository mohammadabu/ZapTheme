odoo.define('theme_zap.snipOption', function (require) {
    'use strict';
    var core = require('web.core');
    var sOptions = require('web_editor.snippets.options');
    var wUtils = require('website.utils');
    var _t = core._t;
    console.log('test_1')
    sOptions.registry.js_get_test_limit = sOptions.Class.extend({
        postsTestLimit: function (previewMode, value, $opt) {
            value = parseInt(value);
            console.log('value')
            console.log(value)
            this.$target.attr('data-posts-test-limit', value).data('postsTestLimit', value);
            this.trigger_up('widgets_start_request', {
                editableMode: true,
                $target: this.$target,
            });

        },
    })
})    
    