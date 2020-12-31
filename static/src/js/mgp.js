odoo.define('mgp.plainte', function (require) {
    "use strict";

    var FormView = require('web.FormView');

    FormView.include({
        init: function(record) {
            this._super.apply(this, arguments);
            console.log('INIT');
            //console.log(record.fields.reference);

            self = this;
            if (this.controllerParams.modelName === 'mgp.plainte') {
                //var plainte = new Model('mgp.plainte');
                //var data = this.model.get(this.handle);
                // var fields = this.field_manager;
                // console.log(fields);

                // if (this.datarecord && (this.datarecord.statut === 'state')) {
                //     this.rendererParams.activeActions.edit = false;
                // }      
                //this.rendererParams.activeActions.edit = false;          
                
                //o_form_button_save
                //class=oe_edit_only
            }
        },

        start: function() {
            this._super.apply(this, arguments);
            self = this;
            console.log('START');
        },

        load_record: function(record) {
            this._super.apply(this, arguments);
            self = this;
            console.log('LOAD RECORD');
            
            // if (this.model === 'mgp.plainte') {
            //     if (this.datarecord && (this.datarecord.statut === 'state')) {
            //         this.$buttons.find('.o_form_button_edit').css({'display':'none'});
            //     }
            //     else {
            //         this.$buttons.find('.o_form_button_edit').css({'display':''});
            //     }
            // }
        },
    });
});

// odoo.define('mgp.plainte', function (require) {
//     "use strict";

//     var FormView = require('web.FormView');

//     FormView.include({
        
//         init: function() {
//             this._super.apply(this, arguments);
//             console.log('INIT');
            
//             if (this.controllerParams.modelName === 'mgp.plainte') {
//                 //var plainte = new Model('mgp.plainte');
//                 //var data = this.model.get(this.handle);
//                 // var fields = this.field_manager;
//                 // console.log(fields);

//                 // if (this.datarecord && (this.datarecord.statut === 'state')) {
//                 //     this.rendererParams.activeActions.edit = false;
//                 // }      
//                 //this.rendererParams.activeActions.edit = false;          
                
//                 //o_form_button_save
//                 //class=oe_edit_only
//              }
//         },
//     });
// });

//DESACTIVER LE BUTTON EDIT
// odoo.define('mgp.plainte', function (require) {
    
//     var FormView = require('web.FormView');

//     FormView.include({
//         load_record: function(record) {
//             console.log('--------');
//             this._super.apply(this, arguments);
            
//             if (this.model === 'mgp.plainte') {
//                 console.log(this.get_fields_values().statut);
//                 // if (this.datarecord && (this.datarecord.statut === 'state')) {
//                 //     this.$buttons.find('.o_form_button_edit').css({'display':'none'});
//                 // }
//                 // else {
//                 //     this.$buttons.find('.o_form_button_edit').css({'display':''});
//                 // }
                
//             }
//         },

//         // init: function() {
//         //     this._super.apply(this, arguments);
            
//         //     if (this.controllerParams.modelName === 'mgp.plainte') {
//         //         //var plainte = new Model('mgp.plainte');
//         //         //var data = this.model.get(this.handle);
               

//         //         // if (this.datarecord && (this.datarecord.statut === 'state')) {
//         //         //     this.rendererParams.activeActions.edit = false;
//         //         // }      
//         //         this.rendererParams.activeActions.edit = false;                                                                                                                                                                                                                                                                                                                                                                                      
//         //      }
//         // },
        
        
//     });
// });