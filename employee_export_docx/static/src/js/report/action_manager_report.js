odoo.define("odoo_report_docx.report", function (require) {
    "use strict";

    var core = require("web.core");
    var ActionManager = require("web.ActionManager");
    var CrashManager = require("web.CrashManager");
    var framework = require("web.framework");
    var session = require("web.session");
    var _t = core._t;

    ActionManager.include({

        _downloadReportDocx: function (url) {
            var def = $.Deferred();

            if (!window.open(url)) {
                // AAB: this check should be done in get_file service directly,
                // should not be the concern of the caller (and that way, get_file
                // could return a deferred)
                var message = _t('A popup window with your report was blocked. You ' +
                                 'may need to change your browser settings to allow ' +
                                 'popup windows for this page.');
                this.do_warn(_t('Warning'), message, true);
                }
            return def;
            },

        _triggerDownload: function (action, options, type) {
            var self = this;
            var reportUrls = this._makeReportUrls(action);
            if (type === "docx" || type ==="pdf") {
                this._downloadReportDocx(reportUrls[type], action).then(function () {
                    if (action.close_on_report_download) {
                        var closeAction = {type: 'ir.actions.act_window_close'};
                        return self.doAction(closeAction, _.pick(options, 'on_close'));
                    } else {
                        return options.on_close();
                    }
                });
                return
            }
            return this._super.apply(this, arguments);
        },

        _makeReportUrls: function (action) {
            var reportUrls = this._super.apply(this, arguments);
            reportUrls.docx = '/report/docx/' + action.report_name + '/' + action.context.active_ids;
            return reportUrls;
        },

        _executeReportAction: function (action, options) {
            var self = this;
            if (action.report_type === 'docx') {
                return self._triggerDownload(action, options, 'docx');
            }
            return this._super.apply(this, arguments);
        }
    });

});
