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

class mcisogem_act_excl_benef(osv.osv):
	_name =  "mcisogem.act.excl.benef"
	_description = "Exclusion d acte par beneficiaire"

	_columns = {
		'nomen_prest_id' : fields.many2one('mcisogem.nomen.prest' , 'Acte'),
		'centre_id' : fields.many2one('mcisogem.centre' , 'Centre'),
		'benef_id' : fields.many2one('mcisogem.benef' , 'Bénéficaire' , required=True),

		'nom' : fields.char('Nom' , readonly=True),
		'prenom' : fields.char('Prénoms' , readonly=True),

		'nomen_prest_ids' : fields.many2many('mcisogem.nomen.prest' ,'mcisogem_acte_excl_benef_rel', 'name', 'libelle_court_acte',  'Actes' , required=True),
        'centre_ids' : fields.many2many('mcisogem.centre' ,'mcisogem_centre_excl_benef','name','code_centre','Centres' , required=True),


		'dat_eff_act_exc' : fields.date('Date d \'effet'),
		'dat_res_act_exc' : fields.date('Date de résiliation'),
		'state' : fields.selection([('Ex', 'Exclu'), ('A', 'Annulé')] , 'Statut'),
	}

	_defaults ={
		'dat_eff_act_exc' : time.strftime("%Y-%m-%d", time.localtime()),
		'state' : 'Ex',
	}

	_rec_name ="benef_id"
	
	def button_annuler(self,cr,uid,ids,context):
		
		return ids[0]

	def button_action_annuler(self,cr,uid,ids,context):
		excl_data = self.browse(cr, uid, ids[0], context=context)
		ctx = (context or {}).copy()

		ctx['id_excl'] = ids[0]
		ctx['form_view_ref'] = 'mcisogem_act_res_excl_benef_pop'
		ctx['action'] = 'annul'
		ctx['ids'] = ids
		ctx['state'] = excl_data.state

		return {
		  'name':'Exclusion d\acte par Bénéficaire',
		  'view_type':'form',
		  'view_mode':'form',
		  'res_model':'mcisogem.act.excl.benef',
		  'view_id':False,
		  'target':'new',
		  'type':'ir.actions.act_window',
		  'context':ctx,
		}


	def button_action_exclure(self,cr,uid,ids,context):
		
		return self.write(cr, uid, ids , {'state':'Ex' ,'cod_res_act_exc':0 , 'dat_res_act_exc' : False }, context=context)

	
	def onchange_benef(self,cr,uid,ids,benef_id):
		if benef_id:
			benef =  self.pool.get('mcisogem.histo.benef').search(cr,uid,[('id','=',benef_id)])
			benef_data = self.pool.get('mcisogem.histo.benef').browse(cr,uid,benef)
			v ={}
			v = {'nom' : benef_data.nom , 'prenom' : benef_data.prenom_benef , 'college_id' : benef_data.college_id.id}
			return {'value' : v}



	def check_etat_benef(self,cr,uid, benef_id):
		# cette fonction retourne l'état du benefeciaire qu'on lui passe en paramètre 
		benef =  self.pool.get('mcisogem.histo.benef').search(cr,uid,[('id','=',benef_id)])
		benef_data = self.pool.get('mcisogem.histo.benef').browse(cr,uid,benef)
		return benef_data.statut

	def create(self, cr, uid, data, context=None):

		if context.get('action')=='annul':
			
			self.write(cr, uid, context.get('ids'), {'state':'A' , 'dat_res_act_exc' : data['dat_res_act_exc'],'cod_res_act_exc':1 }, context=context)
			return context.get('ids')

		if data['dat_res_act_exc']==False or data['dat_res_act_exc']=='':

			last_id = False
			actes = data['nomen_prest_ids'][0][2]
			centres = data['centre_ids'][0][2]
			benef = data['benef_id']

			if self.check_etat_benef(cr,uid,benef)=='A':

				for centre in centres:

					centre_data = self.pool.get('mcisogem.centre').browse(cr,uid,centre)

					for acte in actes:

						acte_data  = self.pool.get('mcisogem.nomen.prest').browse(cr,uid,acte)

						if self.check_etat_benef(cr,uid,benef)=='A':

							exclusion_existe = self.pool.get('mcisogem.act.excl.benef').search_count(cr, uid, [('nomen_prest_id', '=', acte) , ('centre_id' , '=' , centre) , ('benef_id','=', benef)])

							if exclusion_existe > 0 :
								raise osv.except_osv('Attention !', "Ce Bénéficaire a déjà été exclu dans l'un des centres choisis.")
								
							else:
								do = self.onchange_benef(cr,uid,data['benef_id'],data['benef_id'])
							
								data['state']  = 'Ex'
								data['nomen_prest_id'] = acte
								data['centre_id'] = centre
								data['dat_res_act_exc']= None

								data['nom'] = do['value']['nom']
								data['prenom'] = do['value']['prenom']
								
								last_id = super(mcisogem_act_excl_benef , self).create(cr, uid, data, context=context)
			
				return last_id


			else:
				raise osv.except_osv('Erreur !', "Ce Bénéficaire n'est plus actif.")


			