"""CORS for web session + call_kw (Flutter Web cookie mode / tooling)."""

from odoo.addons.web.controllers.dataset import DataSet
from odoo.addons.web.controllers.session import Session
from odoo.http import route


class SessionCors(Session):
    @route('/web/session/authenticate', type='json', auth='none', cors='*')
    def authenticate(self, db, login, password, base_location=None):
        return super().authenticate(db, login, password, base_location=base_location)

    @route('/web/session/get_session_info', type='json', auth='user', cors='*')
    def get_session_info(self):
        return super().get_session_info()

    @route('/web/session/destroy', type='json', auth='user', cors='*')
    def destroy(self):
        return super().destroy()


class DataSetCors(DataSet):
    @route(
        ['/web/dataset/call_kw', '/web/dataset/call_kw/<path:path>'],
        type='json',
        auth='user',
        cors='*',
    )
    def call_kw(self, model, method, args, kwargs, path=None):
        return super().call_kw(model, method, args, kwargs, path=path)
