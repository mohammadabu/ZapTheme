odoo.define('faceid_attendance_odoo.faceid_attendance', function (require) {
    "use strict";

    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var field_utils = require('web.field_utils');
    var QWeb = core.qweb;
    var _t = core._t;
    var Dialog = require('web.Dialog');
    var rpc = require('web.rpc');
    var time = require('web.time');


    var MyAttendances2 = AbstractAction.extend({
        contentTemplate: 'BinaryImage',
        events: {
        "click .o_form_binary_file_web_cam": _.debounce(function() {this.webcam_attendance();},
         200, true),
        },

        willStart: function () {
            var self = this;

            var def = this._rpc({
                model: 'hr.employee',
                method: 'search_read',
                args: [[['user_id', '=', this.getSession().uid]], ['attendance_state', 'name', 'hours_today', 'user_id']],
            })
            .then(function (res) {
                self.employee = res.length && res[0];
                if (res.length) {
                    self.hours_today = field_utils.format.float_time(self.employee.hours_today);
                }
            });

        return Promise.all([def, this._super.apply(this, arguments)]);
    },
         webcam_attendance: function () {
           var self = this,
           WebCamDialog = $(QWeb.render("WebCamDialog")),
           img_data;

           Webcam.set({
                width: 320,
                height: 240,
                dest_width: 320,
                dest_height: 240,
                image_format: 'jpeg',
                jpeg_quality: 90,
                force_flash: false,
                fps: 45,
                swfURL: '/web_widget_image_webcam/static/src/js/webcam.swf',
            });

           var dialog = new Dialog(self, {
                size: 'large',
                dialogClass: 'o_act_window',
                title: _t("WebCam Booth"),
                $content: WebCamDialog,
                buttons: [
                    {
                        text: _t("Take Snapshot"), classes: 'btn-primary take_snap_btn',
                        click: function () {
                            Webcam.snap( function(data) {
                                img_data = data;
                                // Display Snap besides Live WebCam Preview
                                WebCamDialog.find("#webcam_result").html('<img src="'+img_data+'"/>');
                            });
                            if (Webcam.live) {
                                // Remove "disabled" attr from "Save & Close" button
                                $('.save_close_btn').removeAttr('disabled');
                                $('.check_in').removeAttr('disabled');
                                $('.check_out').removeAttr('disabled');
                            }
                        }
                    },
                    //      Check in js
                    {
                        text: _t("Check in"), classes: 'btn-primary check_in', close: true,
                        click: function () {
                           var img_data_base64 = img_data.split(',')[1];
                           var def = this._rpc({
                                model: 'hr.employee',
                                method: 'create_time_check_in',
                                args: [[['user_id', '=', this.getSession().uid]]],
                                kwargs: {"image_attendance": img_data_base64,'name_user':self.employee.name,
                                        'id_user':self.employee.user_id},
                            });
                        }
                    },
                    //    Check out js
                    {
                        text: _t("Check out"), classes: 'btn-primary check_out', close: true,
                        click: function () {
                            var img_data_base64 = img_data.split(',')[1];
                            var def = this._rpc({
                                model: 'hr.employee',
                                method: 'create_time_check_out',
                                args: [[['user_id', '=', this.getSession().uid]]],
                                kwargs: {"image_attendance": img_data_base64,'name_user':self.employee.name, 'id_user':self.employee.id },
                            })
                        }
                    },
                    {
                        text: _t("Close"), close: true
                    }
                ]
            }).open();

            dialog.opened().then(function() {
                    Webcam.attach('#live_webcam');

                    // At time of Init "Save & Close" button is disabled
                    $('.save_close_btn').attr('disabled', 'disabled');
                    $('.check_in').attr('disabled', 'disabled');
                    $('.check_out').attr('disabled', 'disabled');

                    // Placeholder Image in the div "webcam_result"
                    WebCamDialog.find("#webcam_result").html('<img src="/web_widget_image_webcam/static/src/img/webcam_placeholder.png"/>');
                });
        },
    });

    core.action_registry.add('faceid_attendance_odoo_my_attendance', MyAttendances2);

    return MyAttendances2;

});