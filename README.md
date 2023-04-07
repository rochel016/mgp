MECANISME DE GESTION DE PLAINTES
By: UGD (EGM) Madagascar
#--------------------------------------
DASHBOARD MOVING

in addons/board/static/src/js/board_view.js

Change the below code:

_saveDashboard: function () {
    var board = this.renderer.getBoard();
    var arch = QWeb.render('DashBoard.xml', _.extend({}, board));
    //console.log("View ID....", this.actionViews[0]['viewID']);
    return this._rpc({
            route: '/web/view/edit_custom',
            params: {
                custom_id: this.customViewID,
                arch: arch,
            }
        }).then(dataManager.invalidate.bind(dataManager));
},

TO

_saveDashboard: function () {
    var board = this.renderer.getBoard();
    var arch = QWeb.render('DashBoard.xml', _.extend({}, board));
    //console.log("View ID....", this.actionViews[0]['viewID']);
    return this._rpc({
            route: '/web/view/edit_custom',
            params: {
                custom_id: this.customViewID != null? this.customViewID: '',
                arch: arch,
                view_id: this.actionViews[0]['viewID'],
            }
        }).then(dataManager.invalidate.bind(dataManager));
},

AND

in: odoo/addons/web/controllers/main.py

@http.route('/web/view/edit_custom', type='json', auth="user")
def edit_custom(self, custom_id, arch):
    """
    Edit a custom view 

    :param int custom_id: the id of the edited custom view
    :param str arch: the edited arch of the custom view
    :returns: dict with acknowledged operation (result set to True)
    """
    custom_view = request.env['ir.ui.view.custom'].browse(custom_id)
    custom_view.write({ 'arch': arch })
    return {'result': True}

TO

    @http.route('/web/view/edit_custom', type='json', auth="user")
def edit_custom(self, custom_id, arch, view_id):
    """
    Edit a custom view 

    :param int custom_id: the id of the edited custom view
    :param str arch: the edited arch of the custom view
    :returns: dict with acknowledged operation (result set to True)
    """
    if custom_id:
        custom_view = request.env['ir.ui.view.custom'].browse(custom_id)
    else:
        custom_view = request.env['ir.ui.view'].browse(view_id)

    custom_view.write({ 'arch': arch })
    return {'result': True}