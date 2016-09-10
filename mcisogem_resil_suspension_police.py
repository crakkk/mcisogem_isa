# -*- coding:utf8 -*-
import time

from openerp import SUPERUSER_ID
from openerp.osv import fields
from openerp.osv import osv
from datetime import datetime, timedelta
from openerp import tools
from openerp.tools.translate import _
import openerp
from dateutil.relativedelta import relativedelta
from dateutil import parser
import logging

# Historique de résiliation des polices
class mcisogem_histo_resil_police(osv.osv):
    _name = "mcisogem.histo.resil.police"
    _description = "Historique de resiliation de police"


    _columns = {
        'police_id' : fields.many2one('mcisogem.police', 'Police', readonly=True),
        'num_interne_pol': fields.integer("N° Police" , readonly=True),
        'lib_action' : fields.char('Action'),
        'dt_action' : fields.datetime('Date d\'action'),
    }

    def _get_context(self, cr, uid, context):
        context = context or {}
        return context.get('police')

    _defaults ={
        'dt_action' : time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        'police_id': _get_context,
    }
    _rec_name =  'police_id'

    def onchange_police(self, cr, uid, ids, police_id, context=None):        
        if not police_id:
            return False
        else:
            v ={}
            police = self.pool.get('mcisogem.police').search(cr, uid, [('id', '=', police_id)])
            police_data = self.pool.get('mcisogem.police').browse(cr, uid, police)
            v= {'num_interne_pol' : police_data.id , 'name' : police_data.name , 'lib_action' : 'Resiliation'}

        return {'value':v}



    def button_resilier_police(self, cr, uid , ids, vals, context=None):
        return True

    def create(self,cr,uid,vals,context=None):
        vals['police_id'] = context.get('police')
        vals['num_interne_pol'] = context.get('num_interne_police')

        if not vals['lib_action']:
            vals['lib_action'] = 'Résiliation'
            
        police = self.pool.get('mcisogem.police').search(cr,uid,[('id' , '=' , context.get('police'))])
        police_data = self.pool.get('mcisogem.police').browse(cr, uid, police)

        self.pool.get('mcisogem.police').write(cr,uid,police_data.ids,{'state':'resil' ,'dt_resil_pol':vals['dt_action']},context=context)

        return super(mcisogem_histo_resil_police , self).create(cr,uid,vals,context)


# implémentation des fonctionnalités suspension police et police sur liste noire terminée