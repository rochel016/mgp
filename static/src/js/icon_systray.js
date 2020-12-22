odoo.define('systray_ticket.systray_ticket', function(require) {
    "use strict";
    var SystrayMenu = require('web.SystrayMenu');
    var Widget = require('web.Widget');
    
    var ajax = require('web.ajax');
    var tickets_count = ""
    var tickets_list = []
    
    
    ajax.jsonRpc("/plainte_notif", 'call').then(function(data) {
        if (data) {
            tickets_count = data["count"]; // console.log(tickets_count);
            //tickets_list = data["tickets"]; //console.log(data["tickets"]);
        } else {
            console.log("No ticket ou Erreur loading ticket");
        }
    });
    
    window.click_num=0;
    var ActionMenu = Widget.extend({
        template: 'systray_ticket.icon',
        events: {
            'click .my_icon': 'onclick_myicon',
        },

        start: function() {
            this._super.apply(this, arguments);
            self = this;
            setTimeout(function(){
                // Show tickets  notification for current user
                if (document.getElementById('tickets_count_id')) 
                    document.getElementById("tickets_count_id").innerHTML = tickets_count;
            }, 50);
        },

        onclick_myicon:function(){
            click_num++;
            $('.toggle-icon').on('click', function() {
                if(click_num%2 != 0) {
                    ajax.jsonRpc("/plainte_notif", 'call').then(function(data) {
                        if (data) {
                            tickets_count = data["count"]; //console.log(tickets_count);
                            tickets_list = data["tickets"]; //console.log(data["tickets"]);

                            setTimeout(function(){
                                // Show tickets  notification for current user
                                document.getElementById("tickets_count_id").innerHTML = tickets_count

                                //Show list tickets notification
                                $("#fa-bell").empty();
                                $("#fa-bell").append("<div class='test_div dropdown dropdown-menu dropdown-menu-right show'><div style='width:250px;'><p><span id='notif_ticket'></span></p></div></div>");
                                var elt = '';
                                for (var index = 0; index < tickets_list.length; ++index) {
                                    elt += '<p class="mgp_systray_notif">' + 'N°' + tickets_list[index][0] + ', ' + tickets_list[index][1] + '</p>';
                                }
                                if (document.getElementById('tickets_count_id'))
                                    document.getElementById("notif_ticket").innerHTML = elt;
                            }, 50);
                        } else {
                            console.log("No ticket ou Erreur loading ticket");
                        }

                        setTimeout(function(){
                            $("#fa-bell").empty();
                        }, 5000);
                    });
                }
                else {
                    $('.test_div').hide();
                }
            });
        },
    });
    SystrayMenu.Items.push(ActionMenu);
    return ActionMenu;
 });