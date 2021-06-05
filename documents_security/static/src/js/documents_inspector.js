odoo.define('documents_security.DocumentsInspector', function (require) {
    "use strict";


    var core = require('web.core');
    var DocumentsInspector = require("documents.DocumentsInspector");
    var session = require('web.session');

    var _t = core._t;

    var DocumentsInspector = DocumentsInspector.include({
        /**
         * Download the selected documents (zipped if there are several documents).
         *
         * @private
         */
        _onDownload: function () {
            self = this;
            $.when(
                session.user_has_group('documents_security.downloader'),
            ).done(function (is_downloader) {
                if (is_downloader) {
                    self.trigger_up('download', {
                        resIDs: _.pluck(self.records, 'res_id'),
                    });
                } else {
                    self.do_warn(_t("Invalid permissions"), _t("You must be part of `Documents / Download` group"));
                }
            });
        },
    });
});
