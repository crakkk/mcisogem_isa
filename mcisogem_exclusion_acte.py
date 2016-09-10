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

class mcisogem_act_excl_pol(osv.osv):
    _name =  "mcisogem.act.excl.pol"
    _description = "Acte exclusion police"

    _columns = {
        'nomen_prest_ids' : fields.many2many('mcisogem.nomen.prest' ,'mcisogem_acte_excl_rel', 'name', 'libelle_court_acte',  'Actes' , required=True),
        'cod_res_act_exc' : fields.char(''),
        'lbc_nonem_prest' : fields.char(''),
        'centre_ids' : fields.many2many('mcisogem.centre' ,'mcisogem_centre_excl_pol','name','code_centre','Centres' , required=True),
        'lbc_centre' : fields.char(''),

        'police_id' : fields.many2one('mcisogem.police' , 'Police' , required=True),

        'dat_eff_act_exc' : fields.date('Date d \'effet'),
        'dat_res_act_exc' : fields.date('Date d\'annulation'),
       
        'state' : fields.selection([('Ex', 'Actif'), ('A', 'Annulé')] , 'Statut'),
    }

    _rec_name = 'police_id'

    def onchange_nomen(self, cr, uid, ids, nonem_id, context=None):
        v = {}
        
        nomen = self.pool.get('mcisogem.nomen.prest').search(cr, uid,[('id', '=', nomen_id)])
        nomen_data = self.pool.get('mcisogem.nomen.prest').browse(cr, uid, nomen)
        v = {'cod_res_act_exc' : nomen_data.id , 'lbc_nonem_prest' : nomen_data.name}
        return {'values : v'}

    def onchange_centre(self, cr, uid, ids, centre_id, context=None):
        v={}
        centre = self.pool.get('mcisogem.centre').search(cr, uid,[('id', '=', centre_id)])
        centre_data = self.pool.get('mcisogem.centre').browse(cr, uid, centre)
        v = {'lbc_centre' : centre_data.name}
        return {'values' : v}


    def button_action_resilier(self, cr, uid, ids, context=None):
        
        # ouvre le formulaire de resiliation d'une exclusion
        excl = self.browse(cr, uid, ids[0], context=context).id

        excl_table = self.search(cr, uid, [('id', '=', excl)])
        excl_data = self.browse(cr,uid,excl_table)

        ctx = (context or {}).copy()

        ctx['id_excl'] = ids[0]
        ctx['ids'] = excl_data.ids
        ctx['form_view_ref'] = 'mcisogem_act_res_excl_pol_pop'

        return {
          'name':'Annuler la resiliation',
          'view_type':'form',
          'view_mode':'form',
          'res_model':'mcisogem.act.excl.pol',
          'view_id':False,
          'target':'new',
          'domain':[('id', '=', excl)],
          'type':'ir.actions.act_window',
          'context':ctx,
          'nodestroy' : True,
        }
    
    def resilier(self, cr, uid, ids,data, context=None):
        return True

    def button_to_exclure(self,cr,uid,ids,context=None):
        return self.write(cr, uid, ids, {'state':'Ex'}, context=context)



    def check_etat_police(self,cr,uid, police_id):
        # cette fonction retourne l'état de la police qu'on lui passe en paramètre 
        police =  self.pool.get('mcisogem.police').search(cr,uid,[('id','=',police_id)])
        police_data = self.pool.get('mcisogem.police').browse(cr,uid,police)
        return police_data.state


    def create(self, cr, uid, data, context=None):

        if data['dat_res_act_exc'] == False:

            acte = data['nomen_prest_ids']
            centre = data['centre_ids']
            police = data['police_id']


            if self.check_etat_police(cr,uid,police)=='draft':
                # nbre =  self.pool.get('mcisogem.act.excl.pol').search_count(cr, uid, [('nomen_prest_ids', '=', acte) , ('centre_ids' , '=' , centre) , ('police_id','=', police)])
                data['state']  = 'Ex'
                data['dat_res_act_exc']= None
                return super(mcisogem_act_excl_pol , self).create(cr, uid, data, context=context)
            else:
                raise osv.except_osv('Erreur !', "Cette police n'est pas active")
                return False
        else:
           cr.execute('update mcisogem_act_excl_pol set state=%s,dat_res_act_exc=%s where id=%s' , ('A' ,data['dat_res_act_exc'], context.get('ids')[0]))

           return context.get('ids')[0]
            # self.write(cr, uid, context.get('ids'), {'state':'A' , 'dat_res_act_exc' : data['dat_res_act_exc']}, context=context)
        
    _defaults ={
        'dat_eff_act_exc' : time.strftime("%Y-%m-%d", time.localtime())
    }

# Fin exclusion d'acte par police 