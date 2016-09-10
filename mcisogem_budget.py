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
class mcisogem_budget(osv.osv):
    _name = "mcisogem.budget"
    _description = "Budget"

    _columns = {
        'num_histo_prime' : fields.integer('N° Historique de Prime'),
        'mnt_budget_restant' : fields.float('Montant Restant' , digits=(18,0)),
        'mnt_budget_simple_rea' : fields.float('Montant Réajusté (sans sida)' , digits=(18,0)),
        'mnt_budget_sida_rea' : fields.float('Montant Simple Réajusté (Avec sida)' , digits=(18,0)),
        
        'type_budget' : fields.selection([('I', 'Initial'), ('R', 'Réajusté')] , 'Type du budget'),

        'statut_budget' : fields.char(''),
        'state' : fields.selection([('A', 'Actif'), ('I', 'Inactif')] , 'Statut'),
        'dt_budget_rea' : fields.date('Date de réajustement'),
    }

    def create(self, cr, uid, vals, context=None):
        vals['statut_budget'] = vals['state']
       
        return super(mcisogem_budget , self).create(cr, uid, vals, context=context)

    def write(self,cr,uid,ids,vals,context=None):
        vals['type_budget'] = 'R'
        return super(mcisogem_budget, self).write(cr, uid,ids,vals, context=context)

    def button_to_activer(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'A' , 'statut_budget':'A'}, context=context)
        return True 

    def button_to_desactiver(self,cr,uid,ids,context=None):
        self.write(cr, uid, ids, {'state':'I' , 'statut_budget':'I'}, context=context)
        return True

class mcisogem_encaissement(osv.osv):
    _name ="mcisogem.encaissement"
    _description = "Encaissement de budget"

    _columns = {
        'num_budget' : fields.integer('N° Budget'),
        'college_id' : fields.many2one('mcisogem.college' , 'College', readonly=True),
        'lbc_college' : fields.char('College'),
        'budget_id' : fields.many2one('mcisogem.budget' , 'Budget'),
        'num_interne_police' : fields.integer('N° Interne police'),
        'police_id' : fields.many2one('mcisogem.police' , 'Police' , readonly=True),
        'lbc_assur' : fields.char(),
        'garant_id' : fields.many2one('mcisogem.garant' , 'Garant', readonly=True),
        'mnt_a_enc' : fields.float('Montant à encaisser' ,  digits=(18, 0) , required=True),
        'mnt_rest'  : fields.float('Montant restant' , digits=(18, 0) , required=True , readonly=True),
        'mnt_enc' : fields.float('Montant encaissé' ,  digits=(18, 0) , required=True),
        'dt_enc' : fields.datetime('Date d\'encaissement'),
        'dt_deb' : fields.datetime('Date de début'),
    }

    def onchange_budget(self, cr, uid, ids, budget_id, context=None):
        
        if budget_id:
            v = {}
            budget = self.pool.get('mcisogem.budget').search(cr, uid,[('id', '=', budget_id)])
            budget_data = self.pool.get('mcisogem.budget').browse(cr, uid, budget)
            
            histo_prime = self.pool.get('mcisogem.histo.prime').search(cr, uid,[('id', '=', budget_data.num_histo_prime)])

            histo_data = self.pool.get('mcisogem.histo.prime').browse(cr, uid, histo_prime)
            v = {'police_id':histo_data.police_id.id , 'garant_id' : histo_data.garant_id.id , 'college_id' : histo_data.college_id.id}
            
            return {'value' : v}


    def onchange_montant(self, cr, uid, ids, montant_a_encaisser , montant_encaisse , context=None):
        

        v = {}
        if montant_a_encaisser >= 0 and montant_encaisse >= 0:
            
            reste = montant_a_encaisser - montant_encaisse
            if reste < 0 :
                reste = 0
        else:
            reste = 0

        v = {'mnt_rest':reste}
        return {'value' : v}

    def create(self, cr, uid, vals, context=None):

        vals['mnt_rest'] = vals['mnt_a_enc'] - vals['mnt_enc']

        values = self.onchange_budget(cr,uid,1,vals['budget_id'],context)['value']

        vals['police_id'] = values['police_id']
        vals ['garant_id'] = values['garant_id']
        vals['college_id'] = values['college_id']

        college = self.pool.get('mcisogem.college').search(cr, uid,[('id', '=', vals['college_id'])])

        d_college = self.pool.get('mcisogem.college').browse(cr, uid, college)

        vals['lbc_college'] = d_college.name

        vals['num_interne_police'] = vals['police_id']
        assureur = self.pool.get('mcisogem.garant').search(cr, uid,[('id', '=', vals['garant_id'])])
        d_assureur = self.pool.get('mcisogem.college').browse(cr, uid, assureur)

        vals['lbc_assur'] = d_assureur.name
        
        return super(mcisogem_encaissement , self).create(cr, uid, vals, context=context)


# Encaissement et Réajustement de budget
