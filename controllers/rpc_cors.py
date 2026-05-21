"""Enable CORS on /jsonrpc for Flutter Web (cross-origin dev server)."""

from odoo.addons.base.controllers.rpc import RPC
from odoo.http import dispatch_rpc, route


class RPCCors(RPC):
    @route('/jsonrpc', type='json', auth='none', save_session=False, cors='*')
    def jsonrpc(self, service, method, args):
        return dispatch_rpc(service, method, args)
