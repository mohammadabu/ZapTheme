odoo.define('theme_zap.snipOption', function (require) {
    'use strict';
    var core = require('web.core');
    var sOptions = require('web_editor.snippets.options');
    var wUtils = require('website.utils');
    var _t = core._t;
    console.log('test_1')
    sOptions.registry.js_get_test_limit = sOptions.Class.extend({
        start: function () {
            console.log('test_2')
            // var def = this._rpc({
            //     model: 'blog.blog',
            //     method: 'search_read',
            //     args: [wUtils.websiteDomain(this), ['name']],
            // }).then(blogs => {
            //     var allBlogsEl = this.el.querySelector('[data-filter-by-blog-id="0"]');
            //     var menuEl = allBlogsEl.parentNode;
            //     for (const blog of blogs) {
            //         let el = allBlogsEl.cloneNode();
            //         el.dataset.filterByBlogId = blog.id;
            //         el.textContent = blog.name;
            //         menuEl.appendChild(el);
            //     }
            //     this._setActive();
            // });
    
            // return Promise.all([this._super.apply(this, arguments), def]);
        },
        postsLimit: function (previewMode, value, $opt) {
            value = parseInt(value);
            console.log(value)
            this.$target.attr('data-posts-limit', value).data('postsLimit', value);
            // this.trigger_up('widgets_start_request', {
            //     editableMode: true,
            //     $target: this.$target,
            // });

        },
        _setActive: function () {
            this._super.apply(this, arguments);
            var activeLimit = this.$target.data('postsLimit') || 3;
    
            this.$el.find('[data-posts-limit]').removeClass('active');
            this.$el.find('[data-posts-limit=' + activeLimit + ']').addClass('active');
        },
    })
})    
    