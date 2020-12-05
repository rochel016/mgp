odoo.define('systray_ticket.systray_ticket', function(require) {
    "use strict";
    var SystrayMenu = require('web.SystrayMenu');
    var Widget = require('web.Widget');
    window.click_num=0;
    var ActionMenu = Widget.extend({
        template: 'systray_ticket.icon',
        events: {
            'click .my_icon': 'onclick_myicon',
        },
        onclick_myicon:function(){
            click_num++;
            $('.toggle-icon').on('click', function() {
                if(click_num%2 != 0) {
                    $("#fa-bell").append("<div class='test_div dropdown dropdown-menu dropdown-menu-right show'><div style='height:30px;width:250px;'><p>Date/Time:<span id='datetime'></span></p></div></div>");
                    $("#toto").innerHTML = "9";
                    
                    var dt = new Date();
                    document.getElementById("datetime").innerHTML=dt.toLocaleString();
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