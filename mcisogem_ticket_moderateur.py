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




class mcisogem_tick_mod_pol(osv.osv):
	_name ="mcisogem.tick.mod.pol"
	_description ="Ticket moderateur"

	_columns={
		'garant_id':fields.many2one('mcisogem.garant' , 'Garant'),

		'nomen_prest_id' : fields.many2one('mcisogem.nomen.prest',  'Acte' ),
		'lbc_nonem_prest' : fields.char('Acte'), # le libelle de l'acte

		'centre_id' : fields.many2one('mcisogem.centre', 'Centre') ,
		'lbc_centre' : fields.char('Centre'), # le libelle du centre

		'police_id' : fields.many2one('mcisogem.police' , 'Police'),
		'college_id' : fields.many2one('mcisogem.college' , 'Collège'),
		'num_interne_pol' : fields.integer(''), # le code de la police


		'code_acte_temp': fields.many2many('mcisogem.nomen.prest',
										'mcisogem_ticket_nonem_prest_rel_',
										'ticket_nonem_id',
										'id',
										'Choix des actes', required=False),


		'code_centre_temp': fields.many2many('mcisogem.centre',
										'mcisogem_ticket_centre_rel_',
										'ticket_centre_id',
										'id',
										'Choix des centres', required=False),


		'code_police_temp': fields.many2many('mcisogem.police',
										'mcisogem_ticket_police_rel_',
										'ticket_police_id',
										'id',
										'Choix des polices', required=False),
		'code_college_temp': fields.many2many('mcisogem.college' , 'mcisogem_col_tick_rel', 'tick_id' , 'col_id' , 'Collèges'),


		'dt_eff_tick_mod':fields.date('Date d\'effet' , required=True),

		'dt_res_tick_mod' : fields.date('Date de d\'annulation'),

		'mnt_tick_mod':fields.float('Ticket Modérateur', digits=(18,0) , required=True),

		'state' : fields.selection([('N', 'Actif'), ('A', 'Résilié')] , 'Statut'),
		'chargement' : fields.integer(),
		'choix_typ_tick_mod' : fields.boolean('Montant en %'),
		'typ_tick_mod' : fields.integer(''),
		'affichage' : fields.integer(''),
	}


	_rec_name = 'police_id'

	def onchange_garant_id(self, cr, uid, ids, garant_id, context=None):        
		d = {}
		critere = []
		police_ids = self.pool.get('mcisogem.police').search(cr,uid,[('garant_id' , '=' , garant_id )])
		
		if garant_id:
			critere.append(('id' , 'in' , police_ids))
		
		d = {'code_police_temp' : critere}
		return {'domain' : d}




	def onchange_police(self, cr, uid, ids, police_ids, context=None):

		if police_ids[0][2]:

			d = {}
			critere = []
			pol_ids = []
			centre_ids = []
			col_ids = []

			for pol_id in police_ids[0][2]:
				pol_ids.append(pol_id)

				col_id = self.pool.get('mcisogem.college').search(cr,uid,[('police_id' , '=' , pol_id)])

				for i in col_id:
					col_ids.append(i)


			print('***-----***')
			print(col_ids)

			# ss = self.pool.get('mcisogem.tarif.nego.police').search(cr,uid,[('police_id' , 'in' , pol_ids)])

			# for tnp in self.pool.get('mcisogem.tarif.nego.police').browse(cr,uid,ss):
			# 	centre_ids.append(tnp.centre_id.id)

			# if police_ids[0][2]:
			# 	critere.append(('id' , 'in' , centre_ids))
			

			# d = {'code_centre_temp' : critere , 'code_college_temp' : [('id' , 'in' , col_ids)]}

			d = {'code_college_temp' : [('id' , 'in' , col_ids)]}
			return {'domain' : d}



	# def au_chargement(self, cr, uid, context=None):

	# 	cr.execute("delete from mcisogem_ticket_nego_centre_temp where write_uid=%s", (uid,))
	# 	cr.execute("delete from mcisogem_ticket_nego_nomen_prest_temp where write_uid=%s", (uid,))
	# 	cr.execute("delete from mcisogem_ticket_nego_police_temp where write_uid=%s", (uid,))

	# 	cr.execute("select * from mcisogem_centre")
	# 	centres = cr.dictfetchall()

	# 	cr.execute("select * from mcisogem_nomen_prest")
	# 	actes = cr.dictfetchall()

	# 	cr.execute("select * from mcisogem_police")
	# 	polices = cr.dictfetchall()

	# 	if len(centres) > 0:
	# 		for centre in centres:
	# 			cr.execute("insert into mcisogem_ticket_nego_centre_temp(create_uid,create_date,code_centre,mnt_tick_mod, write_uid) values(%s,%s, %s, %s, %s)",(uid,time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),centre['id'], 0, uid))

		
	# 	if len(actes) > 0:
	# 		for acte in actes:
	# 			cr.execute("insert into mcisogem_ticket_nego_nomen_prest_temp(create_uid,create_date,code_acte,mnt_tick_mod, write_uid) values(%s,%s, %s, %s, %s)",(uid,time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), acte['id'], 0, uid))
		
	# 	if len(polices) > 0:

	# 	   for police in polices:
	# 		   cr.execute("insert into mcisogem_ticket_nego_police_temp(create_uid,create_date,code_police,garant_id,mnt_tick_mod, write_uid) values(%s,%s, %s, %s,%s,%s)", (uid,time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),police['id'],police['garant_id'],0, uid))


	def details_police(self,cr,uid, police_id):
		# cette fonctionne retourne les détails sur une police  donnée
		police =  self.pool.get('mcisogem.police').search(cr,uid,[('id','=',police_id)])
		police_data = self.pool.get('mcisogem.police').browse(cr,uid,police)
		return police_data


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


	def check_etat_police(self,cr,uid, police_id):
		# cette fonction retourne l'état de la police qu'on lui passe en paramètre 
		police =  self.pool.get('mcisogem.police').search(cr,uid,[('id','=',police_id)])
		result = self.pool.get('mcisogem.police').search_count(cr,uid,[('id','=',police_id)])
		if result > 0:
			police_data = self.pool.get('mcisogem.police').browse(cr,uid,police)
			return police_data.state
		else:
			return False


	_defaults = {
		'chargement': 1,
		'dt_eff_tick_mod' : time.strftime('%Y-%m-%d', time.localtime()),
		'choix_typ_tick_mod' : False,
	}

	def button_action_resilier(self, cr, uid, ids, context=None):
	   
		# ouvre le formulaire d 'annulation d'un ticket modérateur
		ticket = self.browse(cr, uid, ids[0], context=context).id

		ticket_table = self.search(cr, uid, [('id', '=', ticket)])
		ticket_data = self.browse(cr,uid,ticket_table)

		ctx = (context or {}).copy()

		ctx['id_tick'] = ids[0]
		ctx['ids'] = ticket_data.ids
		ctx['form_view_ref'] = 'mcisogem_annul_tick_mod_pol_form'

		return {
		  'name':'Annulation d\'un ticket modérateur',
		  'view_type':'form',
		  'view_mode':'form',
		  'view_id':False,
		  'target':'new',
		  'type':'ir.actions.act_window',
		  'context':ctx,
		  'res_model':'mcisogem.tick.mod.pol',
		}


	def button_negocier(self,cr,uid,ids,context=None):
		return self.write(cr, uid, ids, {'state':'N'}, context=context)

	def button_resilier(self,cr,uid,ids,context):
		print('*****************')
	
	def create(self, cr, uid, data, context=None):
		if context.get('id_tick'):

			ctx = (context or {}).copy()
			ctx['id_tick'] = ''
			context = ctx
			data['state'] = 'A'
			super(mcisogem_tick_mod_pol , self).write(cr,uid,context.get('id_tick'),data)
			return context.get('ids')[0]

		if data['choix_typ_tick_mod']:
			if data['mnt_tick_mod'] > 100:
				raise osv.except_osv('Attention !', "La Valeur en '%' ne peut excéder 100.")

		erreur_police = []
		
		if data['dt_res_tick_mod']==False or data['dt_res_tick_mod']=='':

			if data['choix_typ_tick_mod']==True:
				data['typ_tick_mod'] = 1
			else:
				data['typ_tick_mod'] = 0

			last_id = False

			acte = data['code_acte_temp']
			centre = data['code_centre_temp']
			police = data['code_police_temp']
			college = data['code_college_temp']

			data['state']  = 'N'
			data['dt_res_tick_mod']= None
			
			for pol_id in police[0][2]:
				# je  recupere  les données de la police dans sa table temporaire puis je selectionne les données originales dans la table police 
				code_police =pol_id
			  
				pol = self.details_police(cr,uid,code_police)

				if self.check_etat_police(cr,uid,pol.id)=='draft':   
					
					for col_id in college[0][2]:

						for act_id in acte[0][2]:
						   
							code_acte = act_id

							act = self.details_acte(cr,uid,code_acte)
							
							for ctr_id in centre[0][2]:

								code_centre = ctr_id
							   
								ctr = self.details_centre(cr,uid,code_centre)

								ticket_existe = self.pool.get('mcisogem.tick.mod.pol').search_count(cr,uid,[('nomen_prest_id','=',act.id),('centre_id','=',ctr.id),('police_id','=',pol.id)])


								if ticket_existe == 0:

									data['lbc_nonem_prest'] = act.name
									data['nomen_prest_id'] = act.id
									data['college_id'] = col_id
									data['centre_id'] = ctr.id
									data['lbc_centre'] = ctr.name

									data['police_id'] = pol.id
									data['num_interne_pol'] = pol.num_interne_police

									data['affichage']=1

									last_id = super(mcisogem_tick_mod_pol , self).create(cr, uid, data, context=context)
								
			if last_id:
				return last_id

			else:
				raise osv.except_osv('Attention !',  "Les éléments que vous tentez de créer existent déjà." )

		else:
			ctx = (context or {}).copy()
			ctx['dt_res_tick_mod'] = data['dt_res_tick_mod']
			self.write(cr, uid, context.get('ids'), {'state':'A' , 'dt_res_tick_mod' : data['dt_res_tick_mod']}, context=context)
			return context.get('ids')[0]

class mcisogem_ticket_nego_nomen_prest_temp(osv.osv):
	_name = "mcisogem.ticket.nego.nomen.prest.temp"
	_description = 'ticket Acte'
	_columns = {
		'code_acte': fields.many2one('mcisogem.nomen.prest', "Acte", required=True, readonly=True),
		'mnt_tick_mod': fields.integer('Ticket Modérateur', required=True),
	}
	_rec_name="code_acte"

class mcisogem_ticket_nego_centre_temp(osv.osv):
	_name = "mcisogem.ticket.nego.centre.temp"
	_description = 'ticket Centre'
	_columns = {
		'code_centre': fields.many2one('mcisogem.centre', "Centre", required=True, readonly=True),
		'mnt_tick_mod': fields.integer('Ticket Modérateur', required=True),
	}
	_rec_name="code_centre"

class mcisogem_ticket_nego_police_temp(osv.osv):
	_name = "mcisogem.ticket.nego.police.temp"
	_description = 'ticket Nego'
	_columns = {
		'code_police': fields.many2one('mcisogem.police', "Police", readonly=True),
		'mnt_tick_mod': fields.integer('Ticket Modérateur'),
		'garant_id' : fields.many2one('mcisogem.garant' , 'Garant'),
	}
	_rec_name="code_police"
