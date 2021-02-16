/**
 * Manage tickets notification
 */
odoo.define('mgp.ticket_systray', function (require) {
    'use strict';
    var session = require('web.session');
    var SystrayMenu = require('web.SystrayMenu');
    var Widget = require('web.Widget');
    var ajax = require('web.ajax');
    var current_view_id = 0;

    var TicketSystray = Widget.extend({
        name: 'demo_days_menu',
        template: 'mgp.ticket_systray',
        events: {
            'show.bs.dropdown': '_onShow',
            'hide.bs.dropdown': '_onHide',
            'click .click-edit': '_do_edit',
        },

        start: function() {
            var self = this;
            self._super.apply(self, arguments); // ???
            return Promise.all([this._super.apply(this, arguments)]).then(function () {
                ajax.jsonRpc("/plainte_notif", 'call').then(function(data) {
                    if (data) {
                        // Recuperer le view_id cu current user
                        current_view_id = parseInt(data["view_id"]);
                        
                        // Recupérer le nombre de tickets du current user
                        let tickets_count = data["count"];

                        // Récupérer la lsite des tickets du current user
                        let tickets_list = data["tickets"];

                        setTimeout(function(){
                            // Update the number of tickets to process
                            self.$('.o_mgp_counter').text(tickets_count);

                            // Clear list
                            self.$('.tickets_list_notif').empty();

                            // Load the list of tickets to be processed
                            for (var index = 0; index < tickets_list.length; ++index) {
                                let id = tickets_list[index][0];
                                let reference = tickets_list[index][1];
                                let message = tickets_list[index][2]
                                
                                // Each ticket to be processed
                                self.$('.tickets_list_notif').append('<button type="button" class="btn btn-primary btn-xs click-edit" style="width: 100%; border-radius: 2px;" data-id="' + id + '" data-ref="' + reference + '">' + message + '</button><div style="height: 1px;"><div/>');
                            }
                        },  50);
                    }
                });
            });
        },

        _do_edit:function (e) {
            e.stopPropagation();
            e.preventDefault();
            
            if (current_view_id <= 0) return;
            
            var self = this;
            let type = e.target.getAttribute("type");
            let id = e.target.getAttribute("data-id");
            let reference = e.target.getAttribute("data-ref");

            if (type === "button" && parseInt(id) > 0 && reference !== "") {
                // Open Form View for editing
                self.do_action({
                    name: 'Plaintes réf:' + reference,
                    type: 'ir.actions.act_window',
                    view_type: 'form',
                    view_mode: 'form',
                    views: [[current_view_id, 'form']],
                    res_model: 'mgp.plainte',
                    res_id: parseInt(id),
                    target: 'current',
                    //nodestroy: true,
                    flags: {'form': {'action_buttons': true, 'options': {'mode': 'edit'}}}
                },{
                    on_reverse_breadcrumb: function () { 
                        //return location.reload();
                    },
                    on_close: function () {
                        //return location.reload();
                    }
                });
            }
        },

        _onShow: function () {
            document.body.classList.add('modal-open');
        },

        _onHide: function () {
            document.body.classList.remove('modal-open');
        },

    });

    TicketSystray.prototype.sequence = 100;
    SystrayMenu.Items.push(TicketSystray);
    return TicketSystray;
});

/**
 * Shedule to update systray icons tickets
 */
odoo.define('schedule.udpate_ticket_systray', function(require) {
    "use strict";

    var ajax = require('web.ajax');

    function RefreshSystrayIcon() {
        ajax.jsonRpc("/plainte_notif", 'call').then(function(data) {
            if (data) {
                let tickets_count = data["count"];
                let tickets_list = data["tickets"];
                setTimeout(function(){
                    // Update the number of tickets to process
                    self.$('.o_mgp_counter').text(tickets_count);
    
                    // Clear list
                    self.$('.tickets_list_notif').empty();

                    // Load the list of tickets to be processed
                    for (var index = 0; index < tickets_list.length; ++index) {
                        let id = tickets_list[index][0];
                        let reference = tickets_list[index][1];
                        let message = tickets_list[index][2]
                        
                        // Each ticket to be processed
                        self.$('.tickets_list_notif').append('<button type="button" class="btn btn-primary btn-xs click-edit" style="width: 100%; border-radius: 2px;" data-id="' + id + '" data-ref="' + reference + '">' + message + '</button><div style="height: 1px;"><div/>');
                    }
                },  50);
            }
        });
    }

    // Refresh systray icon each X seconds
    setInterval(RefreshSystrayIcon, 5000); // 5 seconds
});