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

class mcisogem_tarif_nego_benef(osv.osv):
	_name = "mcisogem.tarif.nego.benef"
	_description= "Tarif negocie par centre et par benef"

	def chargement(self, cr, uid, context):
		cr.execute("delete from mcisogem_tarif_nego_benef_centre_temp where write_uid=%s", (uid,))
		cr.execute("delete from mcisogem_tarif_nego_benef_nomen_prest_temp where write_uid=%s", (uid,))
		cr.execute("delete from mcisogem_tarif_nego_benef_benef_temp where write_uid=%s", (uid,))


		cr.execute("select * from mcisogem_centre")
		centres = cr.dictfetchall()

		if len(centres) > 0:
			for centre in centres:
				cr.execute("insert into mcisogem_tarif_nego_benef_centre_temp(create_uid,create_date,code_centre,mont_brut_tarif, write_uid) values(%s,%s, %s, %s, %s)",(uid,time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),centre['id'], 0, uid))

		cr.execute("select * from mcisogem_nomen_prest")
		actes = cr.dictfetchall()

		if len(actes) > 0:
			for acte in actes:
				cr.execute("insert into mcisogem_tarif_nego_benef_nomen_prest_temp(create_uid,create_date,code_acte,mont_brut_tarif, write_uid) values(%s,%s, %s, %s, %s)",(uid,time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), acte['id'], 0, uid))

		cr.execute("select * from mcisogem_benef")
		benefeciaires = cr.dictfetchall()

		if len(benefeciaires) > 0:
			for benef in benefeciaires:
				cr.execute("insert into mcisogem_tarif_nego_benef_benef_temp(create_uid,create_date,code_benef,prenom,college_id,mont_brut_tarif, write_uid) values(%s,%s,%s,%s, %s, %s,%s)" , (uid,time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),benef['id'],benef['prenom_benef'] + ' ' + benef['nom'],benef['college_id'],0,uid))


	_columns={
		'benef_id' : fields.many2one('mcisogem.benef' , 'Bénéficaire'),
		'matric_benef' : fields.integer(''),
		'prenom' : fields.char('Nom & Prenoms' , readonly=True),
		'college_id':fields.char('College' , readonly=True),
		'tarif' : fields.integer('Tarif' , required=True),
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


		'code_acte_temp_ids': fields.many2many('mcisogem.nomen.prest',
										'mcisogem_tarif_benef_nonem__rel',
										'tarif_nonem_id',
										'id',
										'Choix des actes', required=True),


		'code_centre_temp_ids': fields.many2many('mcisogem.centre',
										'mcisogem_tarif_benef_centre__rel',
										'tarif_centre_id',
										'id',
										'Choix des centres', required=True),


		'code_benef_temp_ids': fields.many2many('mcisogem.benef',
										'mcisogem_tarif_benef_benef__rel',
										'tarif_police_temp_id',
										'id',
										'Choix des beneficiaires', required=True),

		'state' : fields.selection([('N', 'Négocié'), ('A', 'Annulé')] , 'Statut'),
		'affichage' : fields.integer(),
	}

	_defaults = {
		'affichage': 0  ,
		# 'chargement': chargement,
		'dt_eff_tarif_benef' : time.strftime('%Y-%m-%d', time.localtime()),
		'state' : 'N'
	}

	_rec_name = "benef_id"


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

	def button_annuler(self, cr, uid, ids, context=None):
		return True

	def button_negocier(self, cr, uid, ids, context=None):
		return self.write(cr, uid, ids, {'state':'N' ,'cod_res_tarif_benef':0}, context=context)

	def button_action_annuler(self, cr, uid, ids, context=None):
		tarif_data = self.browse(cr, uid, ids[0], context=context)

		ctx = (context or {}).copy()

		ctx['ids'] = tarif_data.ids
		ctx['form_view_ref'] = 'mcisogem_tarif_annul_nego_benef_form'

		return {
		  'name':'Annuler une négociation de tarif',
		  'view_type':'form',
		  'view_mode':'form',
		  'view_id':False,
		  'target':'new',
		  'type':'ir.actions.act_window',
		  'context':ctx,
		  'res_model':'mcisogem.tarif.nego.benef',
		}


	def create(self, cr, uid, data, context=None):
		last_id = 0

		if data['dt_res_tarif_benef']==False or data['dt_res_tarif_benef']=='':

			acte = data['code_acte_temp_ids']
			centre = data['code_centre_temp_ids']
			benef = data['code_benef_temp_ids']

			data['state']  = 'N'
			data['dt_res_tarif_benef']= None

			for benef_id in benef[0][2]:
				# je  recupere  les données du benef dans sa table temporaire puis je selectionne les données originales dans la table benef
				benef_data = self.pool.get('mcisogem.benef').browse(cr,uid,benef_id)

				if self.check_etat_benef(cr,uid,benef_id)=='A':

					for act_id in acte[0][2]:
					   
						acte_data = self.pool.get('mcisogem.nomen.prest').browse(cr,uid,act_id)


						for ctr_id in centre[0][2]:

							centre_data = self.pool.get('mcisogem.centre').browse(cr,uid,ctr_id)

							tarif_existe = self.pool.get('mcisogem.tarif.nego.benef').search_count(cr,uid,[('nomen_prest_id','=',acte_data.id),('centre_id','=',centre_data.id),('benef_id','=',benef_data.id)])

							if tarif_existe == 0:

							   
								data['libelle_court_acte'] = acte_data.libelle_court_acte
								data['lbc_nonem_prest'] = acte_data.name
								data['nomen_prest_id'] = acte_data.id
								data['cod_res_tarif_benef']=0
								data['centre_id'] = centre_data.id
								data['code_centre'] = centre_data.code_centre
								data['lb_centre'] = centre_data.name

								data['benef_id'] = benef_data.id
								data['prenom'] = benef_data.prenom_benef
								data['matric_benef'] = benef_data.matric_benef
								data['college_id'] = benef_data.college_id

								data['affichage']=1

								last_id = super(mcisogem_tarif_nego_benef , self).create(cr, uid, data, context=context)

			return last_id 
			
		else:
			# on veut annuler la negociation
			data['cod_res_tarif_benef']=0
			ctx = (context or {}).copy()
			ctx['dt_res_tarif_benef'] = data['dt_res_tarif_benef']
			self.write(cr, uid, context.get('ids'), {'state':'A' , 'dt_res_tarif_benef' : data['dt_res_tarif_benef'] , 'cod_res_tarif_benef':0}, context=context)
			return context.get('ids')[0]


			
class mcisogem_tarif_nego_benef_nomen_prest_temp(osv.osv):
	_name = "mcisogem.tarif.nego.benef.nomen.prest.temp"
	_description = 'Tarif Acte'
	_columns = {
		'code_acte': fields.many2one('mcisogem.nomen.prest', "Acte", required=True, readonly=True),
		'mont_brut_tarif': fields.integer('Montant brut tarif', required=True),
	}

	_rec_name="code_acte"


class mcisogem_tarif_nego_benef_centre_temp(osv.osv):
	_name = "mcisogem.tarif.nego.benef.centre.temp"
	_description = 'Tarif Centre'
	_columns = {
		'code_centre': fields.many2one('mcisogem.centre', "Centre", required=True, readonly=True),
		'mont_brut_tarif': fields.integer('Montant brut tarif', required=True),
	}
	_rec_name="code_centre"


class mcisogem_tarif_nego_benef_benef_temp(osv.osv):
	_name = "mcisogem.tarif.nego.benef.benef.temp"
	_description = 'Tarif Nego benef'
	_columns = {
		'code_benef': fields.many2one('mcisogem.benef', "Matricule", readonly=True),
		'prenom' : fields.char('Nom & Prénoms' , readonly=True),
		'college_id':fields.char('College' , readonly=True),
		'mont_brut_tarif': fields.integer('Montant brut tarif'),
	}
	_rec_name="code_benef"