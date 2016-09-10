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
_logger = logging.getLogger(__name__)

class mcisogem_tick_mod_nego_benef(osv.osv):
	_name="mcisogem.tick.mod.nego.benef"
	_description="Ticket Moderateur beneficaire"

	_columns={
		'benef_id' : fields.many2one('mcisogem.benef' , 'Bénéficaire'),
		'matric_benef' : fields.integer(''),
		'prenom' : fields.char('Prenoms' , readonly=True),
		'college_id':fields.char('College' , readonly=True),

		'nomen_prest_id' : fields.many2one('mcisogem.nomen.prest',  'Acte'),
		'libelle_court_acte': fields.char(''),  # code de l acte
		'lbc_nonem_prest' : fields.char('Acte'), # le libelle de l'acte

		'code_centre' : fields.char(), # le code du centre
		'centre_id' : fields.many2one('mcisogem.centre', 'Centre'),
		'lb_centre' : fields.char('Centre'), # le libelle du centre

		'chargement':fields.integer(''),
		'dt_eff_tarif_benef' : fields.date('Date d\'effet du tarif'),
		'dt_res_tarif_benef' : fields.date('Date de resiliation du tarif'),

		'cod_res_tarif_benef' : fields.integer(''),


		'code_acte_temp_ids': fields.many2many('mcisogem.ticket.nego.benef.nomen.prest.temp',
										'mcisogem_ticket_benef_nonem_rel',
										'ticket_nonem_id',
										'id',
										'Choix des actes', required=False),


		'code_centre_temp_ids': fields.many2many('mcisogem.ticket.nego.benef.centre.temp',
										'mcisogem_ticket_benef_centre_rel',
										'ticket_centre_id',
										'id',
										'Choix des centres', required=False),


		'code_benef_temp_ids': fields.many2many('mcisogem.ticket.nego.benef.benef.temp',
										'mcisogem_ticket_benef_benef_rel',
										'ticket_police_temp_id',
										'id',
										'Choix des beneficiaires', required=False),



		# 'code_college_temp_ids' : fields.many2many('mcisogem.ticket.nego.benef.college.temp',
		# 								'mcisogem_ticket_benef_college_rel',
		# 								'ticket_college_temp_id',
		# 								'id',
		# 								'Choix des beneficiaires', required=False),


		'dt_eff_tick_mod_benef':fields.date('Date d\'effet' , required=True),

		'dt_res_tick_mod_benef' : fields.date('Date de d\'annulation'),

		'mnt_tick_mod_benef':fields.float('Ticket Modérateur', digits=(18,0) , required=True),

		'choix_typ_tick_mod_benef' : fields.boolean('Montant en %'),

		'typ_tick_mod_benef' : fields.integer(''),
		
		'state' : fields.selection([('N', 'Négocié'), ('A', 'Annulé')] , 'Statut'),
		'affichage' : fields.integer(),
	}

	_rec_name = "benef_id"


	def au_chargement(self, cr, uid, context):
		
		cr.execute("delete from mcisogem_ticket_nego_benef_centre_temp where write_uid=%s", (uid,))
		cr.execute("delete from mcisogem_ticket_nego_benef_nomen_prest_temp where write_uid=%s", (uid,))
		cr.execute("delete from mcisogem_ticket_nego_benef_benef_temp where write_uid=%s", (uid,))
		# cr.execute("delete from mcisogem_ticket_nego_benef_college_temp where write_uid=%s", (uid,))


		cr.execute("select * from mcisogem_centre")
		centres = cr.dictfetchall()

		if len(centres) > 0:
			for centre in centres:
				cr.execute("insert into mcisogem_ticket_nego_benef_centre_temp(create_uid,create_date,code_centre,mont_tick, write_uid) values(%s,%s, %s, %s, %s)",(uid,time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),centre['id'], 0, uid))

		cr.execute("select * from mcisogem_nomen_prest")
		actes = cr.dictfetchall()

		if len(actes) > 0:
			for acte in actes:
				cr.execute("insert into mcisogem_ticket_nego_benef_nomen_prest_temp(create_uid,create_date,code_acte,mont_tick, write_uid) values(%s,%s, %s, %s, %s)",(uid,time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), acte['id'], 0, uid))

		cr.execute("select * from mcisogem_benef")
		benefeciaires = cr.dictfetchall()

		if len(benefeciaires) > 0:
			for benef in benefeciaires:
				cr.execute("insert into mcisogem_ticket_nego_benef_benef_temp(create_uid,create_date,code_benef,matric_benef,prenom,college_id,mont_tick, write_uid) values(%s,%s,%s,%s, %s, %s,%s,%s)" , (uid,time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),benef['id'],benef['matric_benef'],benef['prenom_benef'],benef['college_id'],0,uid))



		cr.execute("select * from mcisogem_college")
		colleges = cr.dictfetchall()

		# if len(colleges) > 0:
		# 	for college in colleges:
		# 		cr.execute("insert into mcisogem_ticket_nego_benef_college_temp(create_uid,create_date,code_college,name,mont_tick, write_uid) values(%s,%s,%s,%s, %s, %s,%s,%s)" , (uid,time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),college['code_college'],college['name'],0,uid))


	_defaults = {
		'chargement' : au_chargement,
		'dt_eff_tick_mod_benef' : time.strftime('%Y-%m-%d', time.localtime()),
		'choix_typ_tick_mod_benef' : False,
	}
	



	def details_centre(self,cr,uid, centre_id):
		# cette fonction retourne les détails sur un centre donné 
		centre =  self.pool.get('mcisogem.centre').search(cr,uid,[('id','=',centre_id)])
		centre_data = self.pool.get('mcisogem.centre').browse(cr,uid,centre)
		return centre_data

	
	def details_acte(self,cr,uid, acte_id):
		# cette fonction retourne les détails sur un acte donné 
		acte =  self.pool.get('mcisogem.nomen.prest').search(cr,uid,[('id','=',acte_id)])
		acte_data = self.pool.get('mcisogem.nomen.prest').browse(cr,uid,acte)
		return acte_data

	def details_benef(self,cr,uid, benef_id):
		# cette fonction retourne les détails sur un beneficiaire donné 
		benef =  self.pool.get('mcisogem.benef').search(cr,uid,[('id','=',benef_id)])
		benef_data = self.pool.get('mcisogem.benef').browse(cr,uid,benef)
		return benef_data

	def check_etat_benef(self,cr,uid, benef_id):
		# cette fonction retourne l'état du benefeciaire qu'on lui passe en paramètre 
		benef =  self.pool.get('mcisogem.benef').search(cr,uid,[('id','=',benef_id)])
		benef_data = self.pool.get('mcisogem.benef').browse(cr,uid,benef)
		return benef_data.statut

	def button_action_annuler(self, cr, uid, ids, context=None):

		ticket_data = self.browse(cr, uid, ids[0], context=context)

		ctx = (context or {}).copy()

		ctx['ids'] = ticket_data.ids
		ctx['form_view_ref'] = 'mcisogem_tick_annul_mod_pol_benef_form'

		return {
		  'name':'Annulation d\'un ticket modérateur',
		  'view_type':'form',
		  'view_mode':'form',
		  'view_id':False,
		  'target':'new',
		  'type':'ir.actions.act_window',
		  'context':ctx,
		  'res_model':'mcisogem.tick.mod.nego.benef',
		}

	def button_negocier(self,cr,uid,ids,context=None):
		return self.write(cr, uid, ids, {'state':'N'}, context=context)

	def button_annuler(self,cr,uid,ids,context):
		return True


	def create(self, cr, uid, data, context=None):

		if data['choix_typ_tick_mod_benef']:
			if data['mnt_tick_mod_benef'] > 0:
				raise osv.except_osv('Attention !', "La Valeur en '%' ne peut excéder 100 !")


		if data['dt_res_tick_mod_benef']==False or data['dt_res_tick_mod_benef']=='':

			if data['choix_typ_tick_mod_benef']==True:
				data['typ_tick_mod_benef'] = 1
			else:
				data['typ_tick_mod_benef'] = 0

			last_id = 0

			acte = data['code_acte_temp_ids']
			centre = data['code_centre_temp_ids']
			benef = data['code_benef_temp_ids']

			data['state']  = 'N'
			data['dt_res_tick_mod_benef']= None

			for bnf_id in benef[0][2]:
				# je  recupere  les données de la police dans sa table temporaire puis je selectionne les données originales dans la table police 

				benef_temp =  self.pool.get('mcisogem.ticket.nego.benef.benef.temp').search(cr,uid,[('id','=',bnf_id)])
				benef_temp_data = self.pool.get('mcisogem.ticket.nego.benef.benef.temp').browse(cr,uid,benef_temp)
				code_benef = benef_temp_data.code_benef.id
			  
				bnf = self.details_benef(cr,uid,code_benef)

				if self.check_etat_benef(cr,uid,bnf.id)=='A':   
					for act_id in acte[0][2]:
					   
						acte_temp =  self.pool.get('mcisogem.ticket.nego.benef.nomen.prest.temp').search(cr,uid,[('id','=',act_id)])
						acte_temp_data = self.pool.get('mcisogem.ticket.nego.benef.nomen.prest.temp').browse(cr,uid,acte_temp)
						code_acte = acte_temp_data.code_acte.id

						act = self.details_acte(cr,uid,code_acte)

						for ctr_id in centre[0][2]:

							centre_temp = self.pool.get('mcisogem.ticket.nego.benef.centre.temp').search(cr,uid,[('id','=',ctr_id)])
							centre_temp_data = self.pool.get('mcisogem.ticket.nego.benef.centre.temp').browse(cr,uid,centre_temp)
							code_centre = centre_temp_data.code_centre.id
						   
							ctr = self.details_centre(cr,uid,code_centre)

							ticket_existe = self.pool.get('mcisogem.tick.mod.nego.benef').search_count(cr,uid,[('nomen_prest_id','=',act.id),('centre_id','=',ctr.id),('benef_id','=',bnf.id)])

							if ticket_existe == 0:

								data['lbc_nonem_prest'] = act.name
								data['nomen_prest_id'] = act.id

								data['centre_id'] = ctr.id
								data['code_centre'] = ctr.code_centre
								data['lb_centre'] = ctr.name

								data['benef_id'] = bnf.id
								data['prenom'] = bnf.prenom_benef
								data['matric_benef'] = bnf.matric_benef
								data['college_id'] = bnf.college_id

								data['affichage']=1

								data['cod_res_tarif_benef'] = 0
								last_id = super(mcisogem_tick_mod_nego_benef , self).create(cr, uid, data, context=context)
			return last_id 
			
		else:
			ctx = (context or {}).copy()
			ctx['dt_res_tick_mod_benef'] = data['dt_res_tick_mod_benef']
			self.write(cr, uid, context.get('ids'), {'state':'A' , 'dt_res_tick_mod_benef' : data['dt_res_tick_mod_benef']}, context=context)
			return context.get('ids')[0]




class mcisogem_ticket_nego_benef_nomen_prest_temp(osv.osv):
	_name = "mcisogem.ticket.nego.benef.nomen.prest.temp"
	_description = 'ticket Acte'
	_columns = {
		'code_acte': fields.many2one('mcisogem.nomen.prest', "Acte", required=True, readonly=True),
		'mont_tick': fields.integer('Montant Ticket', required=True),
	}

	_rec_name="code_acte"


class mcisogem_ticket_nego_benef_centre_temp(osv.osv):
	_name = "mcisogem.ticket.nego.benef.centre.temp"
	_description = 'ticket Centre'
	_columns = {
		'code_centre': fields.many2one('mcisogem.centre', "Centre", required=True, readonly=True),
		'mont_tick': fields.integer('Montant Ticket', required=True),
	}
	_rec_name="code_centre"


class mcisogem_ticket_nego_benef_benef_temp(osv.osv):
	_name = "mcisogem.ticket.nego.benef.benef.temp"
	_description = 'ticket Nego benef'
	_columns = {
		'code_benef': fields.many2one('mcisogem.benef', "Bénéficaire", readonly=True),
		'matric_benef' : fields.char('Matricule'),
		'prenom' : fields.char('Prénoms' , readonly=True),
		'college_id':fields.char('College' , readonly=True),
		'mont_tick': fields.integer('Montant Ticket', required=True),
	}
	_rec_name="code_benef"