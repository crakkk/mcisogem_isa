# -*- coding:utf8 -*-
import time
from random import randint
from openerp import SUPERUSER_ID
from openerp.osv import fields
from openerp.osv import osv
from openerp import tools
from openerp.tools.translate import _
import openerp
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta, date

from dateutil import parser
import logging

_logger = logging.getLogger(__name__)

class mcisogem_tranche_age(osv.osv):
	_name = "mcisogem.tranche.age"
	_description = 'Tranche d\'age'
		
	_columns = {
		'name': fields.char('Tranche'),
		'fin_tranche': fields.integer('Fin tranche'),
		'debut_tranche': fields.integer('Début tranche'),
		'code_tranche': fields.integer('Code tranche'),
	}
	_sql_constraints = [('unique_tranche', 'unique(fin_tranche,debut_tranche)', "Cette tranche d'age existe déjà !"), ]



class mcisogem_type_garant(osv.osv):
	_name = "mcisogem.type.garant"
	_description = 'Type garant'
	
	_columns = {
		'code_type_garant': fields.char('Code', size=18, required=True),
		'name': fields.char('Libellé', size=50, required=True),
	}

	_sql_constraints = [('unique_type_garant', 'unique(name)', "Ce type de garant existe déjà !"), ]


class mcisogem_type_intermediaire(osv.osv):
	_name = "mcisogem.type.intermediaire"
	_description = 'Type Intermediaire'
	
	_columns = {
		'name': fields.char('Libellé', size=50, required=True),
	}

	_sql_constraints = [('unique_type_int', 'unique(name)', "Ce type d'intermediaire existe déjà !"), ]


class mcisogem_type_avenant(osv.osv):
	_name = "mcisogem.type.avenant"
	_description = 'Type avenant'
	
	
	_columns = {
		'code_type_avenant': fields.char('Code', size=5, required=True),
		'name': fields.char('Libellé', size=150, required=True),
	}

	_sql_constraints = [('unique_type_ave', 'unique(name)', "Ce type d'avenant existe déjà !"), ]

	
class mcisogem_type_contrat(osv.osv):
	_name = "mcisogem.type.contrat"
	_description = 'Type de contrat'
	
	_columns = {
		'code_type_contrat': fields.integer('Code', required=True),
		'name': fields.char('Libellé', required=True, size=150),
		'cod_tx_comxion': fields.char('Code tx'),
	}
	
	_defaults = {
		'cod_tx_comxion': 1,
	}
	_sql_constraints = [('unique_type_contrat', 'unique(name)', "Ce type de contrat existe déjà !"), ]


class mcisogem_mode_recond(osv.osv):
	_name = "mcisogem.mod.recond"
	_description = 'Mode de reconduction'
	
	_columns = {
		'code_mod_recond': fields.char('Code', required=True),
		'name': fields.char('Libellé', size=150, required=True),
	}

	_sql_constraints = [('unique_mod_recond', 'unique(name)', "Ce mode de reconduction existe déjà !"), ]



class mcisogem_courtier(osv.osv):
	_name = "mcisogem.courtier"
	_description = 'Intermediaire'    
	
	_columns = {
		'code_courtier': fields.char('Code', size=10),
		'name': fields.char('Désignation', size=150, required=True),
		'ville_id': fields.many2one('mcisogem.ville', 'Ville', required=True),
		'adresse': fields.char('Adresse', size=150),
		'mail': fields.char('Email', size=50),
		'code_bp': fields.integer('Code BP'),
		'boite_postale': fields.integer('Boite postale'),
		'telephone': fields.char('Téléphone', size=18),
		'fax': fields.char('Fax', size=50),
		'taux_commission' : fields.float(' Taux de commission (%) '),
		'type_intermediaire':fields.many2one('mcisogem.type.intermediaire' , 'Type Intermédiaire' , required=True),
		'observation': fields.text('Observations', size=20),
		'statut_social': fields.selection([('1', 'Personne physique'), ('2', 'Personne morale')], 'Statut juridique'),
		'Seq_deb_num_pol': fields.integer('deb num police'),
		'Seq_fin_num_pol': fields.integer('deb fin police'),
	}
	
	_defaults = {
		'Seq_deb_num_pol': 0,
		'Seq_fin_num_pol': 0,
	}
	def create(self, cr, uid, vals, context=None):
		res =  super(mcisogem_courtier, self).create(cr, uid, vals, context=context)   
		vals['code_courtier'] = res
		self.write(cr, uid, res, {'code_courtier':res}, context=context)
		return res 
		
	_sql_constraints = [('unique_interm', 'unique(name, ville_id)', "Cet intermediaire existe déjà !"), ]


class mcisogem_motif_suspen(osv.osv):
	_name = "mcisogem.motif.suspen"
	_description = 'Motif Suspension'
	
	_columns = {
		'code_motif': fields.char('Code', size=10),
		'name': fields.char('Libellé', size=30 , required=True),
	}
	
	_sql_constraints = [('unique_motif_1', 'unique(name)', "Ce motif existe déjà !"), ]

	def create(self, cr, uid, data, context=None):
		data['name'] = str(data['name']).upper()
		return super(mcisogem_motif_suspen, self).create(cr, uid, data, context)


class mcisogem_motif_suspen_benef(osv.osv):
	_name = "mcisogem.motif.suspen.benef"
	_description = 'Motif Suspension Benef' 
	
	_columns = {
		'code_motif': fields.char('Code', size=10),
		'name': fields.char('Libellé', size=30 , required=True),
	}

	_sql_constraints = [('unique_motif_2', 'unique(name)', "Ce motif existe déjà !"), ]



class mcisogem_exercice_comptable(osv.osv):
	_name = "mcisogem.exercice.comptable"
	_description = 'Exercice comptable'

	_columns = {
		'date_debut': fields.date('Date debut', required=True),
		'date_fin': fields.date('Date fin', required=True),
		'obs': fields.text('Observations', size=150),
		'name': fields.char('Exercice'),
		'period_ids': fields.one2many('mcisogem.account.period', 'exercice_id', 'Periodes', ondelete='cascade', order='date_start'),
		'state': fields.selection([('draft','Ouvert'), ('done','Clôturé')], 'Statut', readonly=True, copy=False)
	}
	_defaults = {
		'state': 'draft'
	}
	_order = "date_debut, id"

	_sql_constraints = [
		('name_exo_comptable_uniq', 'unique(name,date_debut, date_fin)', 'Cet exercice existe déjà.'),
	]

	def button_cloturer_exercice(self, cr, uid, ids, context=None):
		result = self.browse(cr, uid, ids[0], context=context).id
		cr.execute('update mcisogem_account_period set state=%s where exercice_id=%s', ('done', result, ))
		return self.write(cr, uid, ids, {'state':'done'}, context=context)

	def _check_duration(self, cr, uid, ids, context=None):
		obj_fy = self.browse(cr, uid, ids[0], context=context)
		if obj_fy.date_fin < obj_fy.date_debut:
			return False
		return True

	_constraints = [
		(_check_duration, 'Erreur!\nLa date de début d\'un exercice doit être antérieure à la date de fin.', ['date_fin'])
	]

	def create_period(self, cr, uid, ids, context=None, interval=1):
		period_obj = self.pool.get('mcisogem.account.period')
		for fy in self.browse(cr, uid, ids, context=context):
			ds = datetime.strptime(fy.date_debut, '%Y-%m-%d')
			while ds.strftime('%Y-%m-%d') < fy.date_fin:
				de = ds + relativedelta(months=interval, days=-1)

				if de.strftime('%Y-%m-%d') > fy.date_fin:
					de = datetime.strptime(fy.date_fin, '%Y-%m-%d')

				period_obj.create(cr, uid, {
					'name': ds.strftime('%m/%Y'),
					'code': ds.strftime('%m/%Y'),
					'date_start': ds.strftime('%Y-%m-%d'),
					'date_stop': de.strftime('%Y-%m-%d'),
					'exercice_id': fy.id,
				})
				ds = ds + relativedelta(months=interval)
		return True

	def write(self, cr, uid, ids, vals, context=None):
		data = {}
		if vals.has_key('date_debut'):
			data['date_debut'] = vals['date_debut']
		else:
			data['date_debut'] = self.browse(cr,uid,ids,context).date_debut


		if vals.has_key('date_fin'):
			data['date_fin'] = vals['date_fin']
		else:
			data['date_fin'] = self.browse(cr, uid, ids, context).date_fin

		vals['name'] = data['date_debut'] + "/" + data['date_fin']

		return super(mcisogem_exercice_comptable, self).write(cr, uid, ids, vals, context=context)


	def create(self, cr, uid, data, context=None):
		data['name'] = data['date_debut'] + "/" + data['date_fin']

		db = data['date_debut']
		fn = data['date_fin']

		if db > fn:
			raise osv.except_osv('Attention !', "Le debut de l'exercice ne doit pas être supérieur à la fin.")

		exerice_srch = self.pool.get('mcisogem.exercice.comptable').search(cr, uid, ['&', ('date_debut', '<=', db),
																		   ('date_fin', '>=', fn)])

		if not exerice_srch:

			exerice_srch = self.pool.get('mcisogem.exercice.comptable').search(cr, uid,
																	 ['&', ('date_debut', '<=', db),
																	  ('date_fin', '>=', db)])

			if not exerice_srch:

				exerice_srch = self.pool.get('mcisogem.exercice.comptable').search(cr, uid,
																		 ['&', ('date_debut', '<=', fn),
																		  ('date_fin', '>=', fn)])

				if not exerice_srch:
					exerice_srch = self.pool.get('mcisogem.exercice.comptable').search(cr, uid,
																			 ['&', ('date_debut', '>=', db),
																			  ('date_fin', '<=', fn)])

		if exerice_srch:
			raise osv.except_osv('Attention !',
								 "Veuillez vérifiez que la periode choisie ne soit pas incluse dans un autre exercice.")

		return super(mcisogem_exercice_comptable, self).create(cr, uid, data, context=context)



class mcisogem_exercice(osv.osv):
	_name = "mcisogem.exercice"
	_description = 'Exercice'

	_columns = {
		'date_debut': fields.date('Date debut', required=True),
		'date_fin': fields.date('Date fin', required=True),
		'obs': fields.text('Observations', size=150),
		'name': fields.char('Exercice'),
		'period_ids': fields.one2many('mcisogem.account.period', 'exercice_id', 'Periodes', ondelete='cascade', order='date_start'),
		'state': fields.selection([('draft','Ouvert'), ('done','Clôturé')], 'Statut', readonly=True, copy=False)
	}
	_defaults = {
		'state': 'draft'
	}
	_order = "date_debut, id"

	_sql_constraints = [
		('name_exo_uniq', 'unique(name,date_debut, date_fin)', 'Cet exercice existe déjà.'),
	]

	def button_cloturer_exercice(self, cr, uid, ids, context=None):
		result = self.browse(cr, uid, ids[0], context=context).id
		cr.execute('update mcisogem_account_period set state=%s where exercice_id=%s', ('done', result, ))
		return self.write(cr, uid, ids, {'state':'done'}, context=context)

	def _check_duration(self, cr, uid, ids, context=None):
		obj_fy = self.browse(cr, uid, ids[0], context=context)
		if obj_fy.date_fin < obj_fy.date_debut:
			return False
		return True

	_constraints = [
		(_check_duration, 'Erreur!\nLa date de début d\'un exercice doit être antérieure à la date de fin.', ['date_fin'])
	]

	def create_period(self, cr, uid, ids, context=None, interval=1):
		period_obj = self.pool.get('mcisogem.account.period')
		for fy in self.browse(cr, uid, ids, context=context):
			ds = datetime.strptime(fy.date_debut, '%Y-%m-%d')
			while ds.strftime('%Y-%m-%d') < fy.date_fin:
				de = ds + relativedelta(months=interval, days=-1)

				if de.strftime('%Y-%m-%d') > fy.date_fin:
					de = datetime.strptime(fy.date_fin, '%Y-%m-%d')

				period_obj.create(cr, uid, {
					'name': ds.strftime('%m/%Y'),
					'code': ds.strftime('%m/%Y'),
					'date_start': ds.strftime('%Y-%m-%d'),
					'date_stop': de.strftime('%Y-%m-%d'),
					'exercice_id': fy.id,
				})
				ds = ds + relativedelta(months=interval)
		return True

	def write(self, cr, uid, ids, vals, context=None):
		data = {}
		if vals.has_key('date_debut'):
			data['date_debut'] = vals['date_debut']
		else:
			data['date_debut'] = self.browse(cr, uid, ids, context).date_debut

		if vals.has_key('date_fin'):
			data['date_fin'] = vals['date_fin']
		else:
			data['date_fin'] = self.browse(cr, uid, ids, context).date_fin

		vals['name'] = data['date_debut'] + "/" + data['date_fin']

		return super(mcisogem_exercice, self).write(cr, uid, ids, vals, context=context)


	def create(self, cr, uid, data, context=None):
		data['name'] = data['date_debut'] + "/" + data['date_fin']

		db = data['date_debut']
		fn = data['date_fin']

		if db > fn:
			raise osv.except_osv('Attention !', "Le debut de l'exercice ne doit pas être supérieur à la fin.")

		# exerice_srch = self.pool.get('mcisogem.exercice').search(cr, uid, ['&', ('date_debut', '<=', db),
		# 																   ('date_fin', '>=', fn)])
        #
		# if not exerice_srch:
        #
		# 	exerice_srch = self.pool.get('mcisogem.exercice').search(cr, uid,
		# 															 ['&', ('date_debut', '<=', db),
		# 															  ('date_fin', '>=', db)])
        #
		# 	if not exerice_srch:
        #
		# 		exerice_srch = self.pool.get('mcisogem.exercice').search(cr, uid,
		# 																 ['&', ('date_debut', '<=', fn),
		# 																  ('date_fin', '>=', fn)])
        #
		# 		if not exerice_srch:
		# 			exerice_srch = self.pool.get('mcisogem.exercice').search(cr, uid,
		# 																	 ['&', ('date_debut', '>=', db),
		# 																	  ('date_fin', '<=', fn)])

		# if exerice_srch:
		# 	raise osv.except_osv('Attention !',
		# 						 "Veuillez vérifiez que la periode choisie ne soit pas incluse dans un autre exercice.")

		return super(mcisogem_exercice, self).create(cr, uid, data, context=context)
		
						
	
class mcisogem_avenant(osv.osv):
	_name = "mcisogem.avenant"
	_description = 'Avenant'
		
	
	_columns = {
		# 'type_avenant_id': fields.selection(TYPE_AVENANT, 'Type avenant', required=True),
		'type_avenant_id':fields.many2one('mcisogem.type.avenant', "Type d\'avenant", required=True),
		'name': fields.char(''),
		'police_id': fields.many2one('mcisogem.police', 'Police', required=True),
		'souscripteur_police': fields.many2one('mcisogem.souscripteur', 'Souscripteur', required=True, readonly=True),
		'num_ave_interne_police': fields.integer('Numéro avenant police', readonly=True),
		'calc_prime_ave': fields.selection([('1', 'Avec calcul de prime'), ('0', 'Sans calcul de prime')], 'Mode de calcul'),
		'dt_eff_mod_pol': fields.date('Date émission'),
		'dt_ope_deb_ave': fields.date('Periode motif du'),
		'dt_ope_fin_ave': fields.date('Au'),
		'periode_mvmt_du': fields.date('Periode mouvement du'),
		'periode_mvt_au': fields.date('Au'),
		'dt_deb_exercice_pol': fields.date('Exercice du', readonly=True),
		'dt_fin_exercice_pol': fields.date('Au', readonly=True),
		'date_effet_prime': fields.date('Date éffet prime', readonly=True),
		'date_effet_police': fields.date('Date éffet police', readonly=True),
		'valider': fields.boolean('Valider'),
		'annuler': fields.boolean('Annuler'),
		'date_annuler': fields.date('le'),
		'dt': fields.boolean(''),
		
		'mnt_regl_prime_ave': fields.integer('t'),
		'mnt_emi_ave': fields.integer('t'),
		'dt_anul_ave': fields.date('t'),
		'mnt_quitance_emi': fields.integer('t'),
		'code_avenant_initial': fields.integer('t'),
		'mnt_echea_paiemt': fields.integer('t'),
		'dt_fin_ave': fields.date('t'),
		'prime_cal_ave': fields.char('t'),
		'nbre_echea_paiemt': fields.char('t'),
		'cod_avenant_initial': fields.integer('t'),
		'mnt_echea_paiemt': fields.integer('t'),
		'state': fields.selection([
			('draft', "Nouveau"),
			('valid', "Valider"),
			('anul', "Annuler"),
		])
	}
	

	# _sql_constraints = [('unique_type_avenant_police', 'unique(police_id, typeavenant_id)', "Le type de centre existe déjà !"), ]
	def onchange_annule(self, cr, uid, ids, annuler, context=None):
		if annuler == False:
			return {'value': {'dt': False}}
		else:
			return {'value': {'dt': True}}
	
	def onchange_type_avenant_id(self, cr, uid, ids, type_avenant_id, context=None):
		vals = {}
		if not type_avenant_id:
			return {'value': {'name': False}}
		else:
			obj_ave_data = self.pool.get('mcisogem.type.avenant').browse(cr, uid, type_avenant_id, context=context)
			vals = { 'name': obj_ave_data.code_type_avenant }
		return {'value':vals}
	
	def onchange_police(self, cr, uid, ids, police_id, context=None):
		vals = {}
		if not police_id:
			return {'value': {'libelle_police': False}}
		else:
			obj_police_data = self.pool.get('mcisogem.police').browse(cr, uid, police_id, context=context)
			datedujour = time.strftime("%Y-%m-%d", time.localtime())
			vals = {'souscripteur_police': obj_police_data.souscripteur_id,
					'num_ave_interne_police': obj_police_data.id,
					'dt_deb_exercice_pol': obj_police_data.dt_deb_exercice,
					'dt_fin_exercice_pol': obj_police_data.dt_fin_exercice,
					'dt_eff_mod_pol': obj_police_data.dt_fin_exercice,
					'periode_mvt_au': obj_police_data.dt_fin_exercice,
					'date_effet_police':obj_police_data.dt_deb_exercice,
					'dt_eff_mod_pol':datedujour,
					'dt_ope_fin_ave':obj_police_data.dt_fin_exercice}
		return {'value':vals}
	
	def _get_context(self, cr, uid, context):
		context = context or {}
		return context.get('police')
	
	
	_defaults = {
		'police_id' : _get_context,
		'date_effet_prime' : '1900-01-01',
		'state': 'draft',
		'dt_eff_mod_pol': lambda *a: time.strftime("%Y-%m-%d"),
		'dt_ope_deb_ave': lambda *a: time.strftime("%Y-%m-%d"),
		'periode_mvmt_du': lambda *a: time.strftime("%Y-%m-%d"),
		'mnt_regl_prime_ave': 0,
		'mnt_emi_ave': 0,
		'dt_anul_ave' : '1900-01-01',
		'mnt_echea_paiemt': 0,
		'mnt_quitance_emi': 0,
		'code_avenant_initial': 0,
		'prime_cal_ave': 0,
		'nbre_echea_paiemt': 0,
		'date_annuler' : '1900-01-01',
		'calc_prime_ave' : '1',
	}
	
	def button_to_valid(self, cr, uid, ids, context=None):
		return self.write(cr, uid, ids, {'state':'valid'}, context=context)
	
	def button_to_anul(self, cr, uid, ids, data, context=None):
		return self.write(cr, uid, ids, data, {'state' : 'anul'}, context=context)
	
	def _check_date_mvt(self, cr, uid, ids, context=None):
		for val in self.read(cr, uid, ids, ['periode_mvmt_du'], context=context):
			if val['periode_mvmt_du']:
				if val['periode_mvmt_du'] > val['periode_mvt_au']:
					return False
				
	def _check_date_modif(self, cr, uid, ids, context=None):
		for val in self.read(cr, uid, ids, ['dt_ope_deb_ave'], context=context):
			if val['dt_ope_deb_ave']:
				if val['dt_ope_deb_ave'] > val['dt_ope_fin_ave']:
					return False
				
	def _check_date_emission(self, cr, uid, ids, context=None):
		for val in self.read(cr, uid, ids, ['dt_eff_mod_pol'], context=context):
			if val['dt_eff_mod_pol']:
				if val['dt_eff_mod_pol'] > val['dt_ope_fin_ave']:
					return False
	
	def button_to_cancel(self, cr, uid, ids, context=None):
		self.write(cr, uid, ids, {'state':'done'}, context=context)
		return True
		  
	def create(self, cr, uid, data, context=None):
		# Recuperation de l'exercice de police

		if data['type_avenant_id'] == 1:
			# Si un c'est l'avenant initial qui est sélectionné
			raise osv.except_osv('Attention !', "Un avenant initial existe déjà pour cette police!")

		else:

			data['police_id'] = self._get_context(cr,uid, context)
			cr.execute("select * from mcisogem_exercice_police where police_id=%s order by id desc", (data['police_id'],))
			lesexopolice = cr.dictfetchall()

			nbre_exo_police = self.pool.get('mcisogem.exercice.police').search_count(cr,uid,[('police_id' , '=' , data['police_id'])])
			
			# on verifie si un exercice de police existe pour la police
			if len(lesexopolice) > 0:
				
				nbre_ave_total = self.pool.get('mcisogem.avenant').search_count(cr,uid,[('police_id' , '=' , data['police_id'])])
				
				exercice_police = lesexopolice[0]
				
				# Recuperation de l'avenant sélectionné
				cr.execute("select * from mcisogem_avenant where state !=%s and police_id=%s", ('valid', data['police_id']))
				lesavenants = cr.dictfetchall()


				# on verifie si le même type d'avenant existe pour cette police
				nbre_ave = self.pool.get('mcisogem.avenant').search_count(cr,uid,[('police_id' , '=' , data['police_id']) , ('type_avenant_id' , '=' , data['type_avenant_id'])])
				
				if nbre_ave > 0:
					raise osv.except_osv('Attention !', "Un avenant de même type existe déjà pour cette police !")


				if len(lesavenants) > 0:
					raise osv.except_osv('Attention !', "La police a déjà un avenant non valide. Validez l'ancienne avant de créer un nouveau !")
					return False

				else:
					
					# Controle sur les dates

					# if data['periode_mvmt_du'] >= data['periode_mvt_au']:
					# 	raise osv.except_osv('Attention !', "La date de début de la période de mouvement doit être supérieur à la date de fin !")


					# if data['periode_mvmt_du'] <= exercice_police['date_debut_exercice']:
					# 	raise osv.except_osv('Attention !', "La date de début de la période de mouvement doit être comprise dans l'exercice de la police !")
					

					# if data['periode_mvt_au'] >= exercice_police['date_fin_exercice']:
					# 	raise osv.except_osv('Attention !', "La date de début de la période de mouvement doit être comprise dans l'exercice de la police !")
					
						# Recuperation du dernier avenant de la police
					cr.execute("select * from mcisogem_avenant where police_id=%s order by id desc" , (data['police_id'],))
					avenant = cr.dictfetchall()[0]
					data['num_ave_interne_police'] = nbre_ave_total + 1
					data['souscripteur_police'] = avenant['souscripteur_police']
					data['dt_deb_exercice_pol'] = exercice_police['date_debut_exercice']
					data['dt_fin_exercice_pol'] = exercice_police['date_fin_exercice']
					data['date_effet_police'] = exercice_police['date_debut_exercice']
					data['name'] = self.pool.get('mcisogem.type.avenant').browse(cr,uid,data['type_avenant_id']).name
					return super(mcisogem_avenant, self).create(cr, uid, data, context=context)         
				
			else:
				raise osv.except_osv('Attention !', "Cette police ne possède pas d'exercice de police !")

	
class mcisogem_college(osv.osv):
	_name = "mcisogem.college"
	_description = 'Collège'
	
	_columns = {
		'police_id' : fields.many2one('mcisogem.police' , 'Police' , readonly=True),
		'code_college': fields.char('Code',  required=True),
		'name': fields.char('Libellé', required=True),
	}

	def _get_context(self, cr, uid, context):
		context = context or {}
		return context.get('police')
	
	_defaults = {
		'police_id': _get_context,
	}

	_sql_constraints = [('unique_college', 'unique(name)', "Ce collège existe déjà !"), ]

	def create(self, cr, uid, data, context=None):

		# data['name'] = str(data['name']).upper()

		data['police_id'] = context.get('police')

		self.pool.get('mcisogem.police').write(cr, uid, context.get('police'), {'a_college' : True}, context=context)

		return super(mcisogem_college, self).create(cr, uid, data, context)



class mcisogem_garant(osv.osv):
	_name = "mcisogem.garant"
	_description = 'Garant'
	
	_inherit = ['mail.thread', 'ir.needaction_mixin']

	_mail_post_access = 'read'
	
	def _get_image(self, cr, uid, ids, name, args, context=None):
		result = dict.fromkeys(ids, False)
		for obj in self.browse(cr, uid, ids, context=context):
			result[obj.id] = tools.image_get_resized_images(obj.image, avoid_resize_medium=True)
		return result

	def _set_image(self, cr, uid, ids, name, value, args, context=None):
		return self.write(cr, uid, ids, {'image': tools.image_resize_image_big(value)}, context=context)
	
	_columns = {
		'code_garant': fields.char('Code', size=10),
		'name': fields.char('Libellé', size=150, required=True),
		'ville_id': fields.many2one('mcisogem.ville', 'Ville', required=True),
		'type_garant_id': fields.many2one('mcisogem.type.garant', 'Type garant', required=True),
		'adresse_garant': fields.char('Adresse', size=150),
		'code_boite_postale': fields.integer('Code Boîte postale'),
		'boite_postale': fields.integer('Boite postale'),
		'telephone_garant': fields.char('Téléphone', size=50),
		'fax_garant': fields.char('Fax', size=50),
		'email_garant': fields.char('Email', size=50),
		'correspondant': fields.char('Correspondant', size=150),
		'responsable': fields.char('Responsable', size=150),
		'capital': fields.integer('Capital'),
		'observation': fields.text('Observation', size=250),
		'debut_num_pol': fields.integer('Debut numéro police'),
		'fin_num_pol': fields.integer('Fin numéro police'),
		'st_assur': fields.integer('St assur'),
		'image': fields.binary("Image",
			help="This field holds the image used as image for the product, limited to 1024x1024px."),
		'image_medium': fields.function(_get_image, fnct_inv=_set_image,
			string="Medium-sized image", type="binary", multi="_get_image",
			store={
				'mcisogem.garant': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
			},
			help="Medium-sized image of the product. It is automatically "\
				 "resized as a 128x128px image, with aspect ratio preserved, "\
				 "only when the image exceeds one of those sizes. Use this field in form views or some kanban views."),
		'image_small': fields.function(_get_image, fnct_inv=_set_image,
			string="Small-sized image", type="binary", multi="_get_image",
			store={
				'mcisogem.garant': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
			},
			help="Small-sized image of the product. It is automatically "\
				 "resized as a 64x64px image, with aspect ratio preserved. "\
				 "Use this field anywhere a small image is required."),
		
		'cpta_assur': fields.char('Compte Garant', size=20),
		'cpta_assur_commission': fields.char('Compte garant commission'),
		'cpta_assur_taxe': fields.char('Compte garant taxe', size=20),
		'cpta_prime': fields.char('Compte prime', size=20),
		'num_plage_type_garant': fields.integer('Numero plage type'),
		'cpta_assur_rd': fields.char('Compte assureur ref', size=20),
		'cpta_assurtier': fields.char('Compte Intermediaire', size=50),
		'libelle_cpta_assurtiers_rd': fields.char('Libellé compte Intermediaire', size=50),
		'show_chp': fields.boolean(''),
		'centre_gestion_id' : fields.many2one('mcisogem.centre.gestion' , 'Centre de gestion'),
		'cpt_tp' : fields.char('Compte  Comptabilité TP'),
		'cpt_tp2' : fields.char(''),
		'cpt_tp3' : fields.char(''),
		'cpt_rd' : fields.char('Compte Comptabilité RD'),
		'cpt_rd2' : fields.char(''),
		'cpt_rd3' : fields.char(''),
		'banque_id' : fields.many2one('mcisogem.banque.reglement', 'Banque de règlement'),
		
		'state': fields.selection([
			('draft', "Nouveau"),
			('sent', "Comptabilité"),
			('done', "Informations Comptable"),
			('cancel', "Annuler"),
			('finish', "Terminer"),
		], 'Status', required=True, readonly=True)
	}
	 
	def _needaction_domain_get(self, cr, uid, context=None):
		cr.execute('select gid from res_groups_users_rel where uid=%s', (uid,))
		lesgroups = cr.dictfetchall()
		if len(lesgroups) > 0:
			for group in lesgroups:
				group_obj = self.pool.get('res.groups').browse(cr, uid, group['gid'], context=context)
				if group_obj.name == "RESPONSABLE COMPTABLE" or group_obj.name == "UTILISATEUR COMPTABLE":
					return [('state', '=', 'done')]
			return False
		else:
			return False	


	def _get_group(self, cr, uid, context=None):
		cr.execute('select gid from res_groups_users_rel where uid=%s', (uid,))
		group_id = cr.fetchone()[0]
		group_obj = self.pool.get('res.groups').browse(cr, uid, group_id, context=context)
		if group_obj.name == 'Financial Manager':
			return True
		else:
			return False
	
	_defaults = {
		'debut_num_pol' : 0,
		'fin_num_pol': 0,
		'st_assur': 1,
		'state' : 'draft',
		'show_chp' : _get_group
	}
	_sql_constraints = [
			('garant_uniq', 'unique(name, type_garant_id, ville_id)', 'Ce garant existe déjà !'),
		]
	
	def button_to_sent(self, cr, uid, ids, context=None):
		return self.write(cr, uid, ids, {'state':'done'}, context=context)
	
	def button_to_done(self, cr, uid, ids, data, context=None):
		table = self.search(cr, uid, [('id', '=', ids)])
		table_obj = self.browse(cr, uid, table, context=context)
		if not table_obj.cpt_tp or not table_obj.cpt_rd or not table_obj.banque_id:
			e_mess = "Veuillez renseigner les informations comptable avant la validation"
			raise osv.except_osv(_('Attention !'), _(e_mess))
		else:
			return self.write(cr, uid, ids, {'state' : 'finish'}, context=context)
	
	def button_to_cancel(self, cr, uid, ids, context=None):
		self.write(cr, uid, ids, {'state':'done'}, context=context)
		return True
	
	def create(self, cr, uid, vals, context=None):
		# Détermination du dernier numéro de la plage type garant
		obj = self.pool.get('mcisogem.centre.gestion').search(cr,uid,[('id' , '!=' , 0)])
		gest_obj = self.pool.get('mcisogem.centre.gestion').browse(cr, uid, obj, context=context)
		# vals['name'] = str(vals['name']).upper()
		vals['centre_gestion_id'] = gest_obj[0].id


		# Workflow vers la comptabilité
		vals['state'] = 'done'


		########### envoi des notifications aux utilisateurs comptables
		msg = str("Un nouveau garant vient d'être créé. Vous devez renseigner ses informations comptables.")

		cr.execute("select id from res_groups where name='RESPONSABLE COMPTABLE' or name='UTILISATEUR COMPTABLE'")
		groupe_ids = cr.dictfetchall()

		for groupe_id in groupe_ids:

			groupe_id = groupe_id['id']
			
			cr.execute('select uid from res_groups_users_rel  where gid=%s', (groupe_id,))

			user_ids = cr.fetchall()

			les_ids = []
			for u_id in user_ids:
				les_ids.append(u_id[0])

			res_users = self.pool['res.users']
			partner_ids = list(set(u.partner_id.id for u in res_users.browse(cr, uid, les_ids , context)))

			self.message_post(
				cr, uid, False,
				body=msg ,
				partner_ids=partner_ids,
				subtype='mail.mt_comment',
				subject="[ISA-WEB] - Validation Comptable",
				context=context
				)

		###################################################""


		
		res =  super(mcisogem_garant, self).create(cr, uid, vals, context=context)   
		vals['code_garant'] = res
		self.write(cr, uid, res, {'code_garant':res}, context=context)
		return res 

	def write(self, cr, uid, ids, vals, context=None):
		if "capital" in vals or "cpta_assur" in vals or "cpta_assur_rd" in vals or "cpta_assur_commission" in vals or "cpta_assur_taxe" in vals or "cpta_prime" in vals or "cpta_prime" in vals or "cpta_assurtier" in vals or "libelle_cpta_assurtiers_rd" in vals:

			vals['state'] = 'finish'

		return super(mcisogem_garant, self).write(cr, uid, ids, vals, context=context)
	
	
class mcisogem_souscripteur(osv.osv):
	_name = "mcisogem.souscripteur"

	_inherit = ['mail.thread']

	_mail_post_access = 'read'

	_description = 'Souscripteur'

	PAIEM_SELECTION = [
		('cheque', 'Chèque'),
		('espece', 'Espèce'),
		('virement', 'Virement'),
		('autres', 'Autres')
	]
	
	def _get_image(self, cr, uid, ids, name, args, context=None):
		result = dict.fromkeys(ids, False)
		for obj in self.browse(cr, uid, ids, context=context):
			result[obj.id] = tools.image_get_resized_images(obj.image, avoid_resize_medium=True)
		return result

	def _set_image(self, cr, uid, ids, name, value, args, context=None):
		return self.write(cr, uid, ids, {'image': tools.image_resize_image_big(value)}, context=context)
	
	_columns = {
		'name': fields.char('Libellé', size=100, required=True),
		'ville_id': fields.many2one('mcisogem.ville', 'Ville', required=True),
		'adresse_souscripteur': fields.char('Adresse', size=60),
		'code_boite_postale': fields.integer('Code Boite postale'),
		'boite_postale': fields.integer('Boite postale'),
		'telephone': fields.char('Téléphone', size=30),
		'fax': fields.char('Fax', size=30),
		'email': fields.char('Email', size=50),
		
		'image': fields.binary("Image",
			help="This field holds the image used as image for the product, limited to 1024x1024px."),
		'image_medium': fields.function(_get_image, fnct_inv=_set_image,
			string="Medium-sized image", type="binary", multi="_get_image",
			store={
				'mcisogem.souscripteur': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
			},
			help="Medium-sized image of the product. It is automatically "\
				 "resized as a 128x128px image, with aspect ratio preserved, "\
				 "only when the image exceeds one of those sizes. Use this field in form views or some kanban views."),
		'image_small': fields.function(_get_image, fnct_inv=_set_image,
			string="Small-sized image", type="binary", multi="_get_image",
			store={
				'mcisogem.souscripteur': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
			},
			help="Small-sized image of the product. It is automatically "\
				 "resized as a 64x64px image, with aspect ratio preserved. "\
				 "Use this field anywhere a small image is required."),
		
		'banque_id': fields.many2one('mcisogem.banque', 'Banque'),
		'mod_paiem': fields.selection(PAIEM_SELECTION, 'Mode de paiement', select=True),
		'num_compte': fields.char('Numéro Compte', size=30),
		'num_guichet': fields.char('Numéro Guichet', size=30),
		'num_compte_interne': fields.char('Numero Compte interne', size=30),
		'cle_rib': fields.char('Cle R.I.B.', size=30),
		'mass_sal_souscr': fields.char('mass sal souscr'),
		
		'affiche': fields.boolean(''),
			  
		'state': fields.selection([
			('draft', "Nouveau"),
			('sent', "Comptabilité"),
			('done', "Informations Comptable"),
			('cancel', "Annuler"),
			('finish', "Terminer"),
		], 'Status', required=True, readonly=True)
	}
	


	_sql_constraints = [('unique_souscripteur', 'unique(name , ville_id)', "Ce souscripteur existe déjà !"), ]


	def _get_group(self, cr, uid, context=None):
		cr.execute('select gid from res_groups_users_rel where uid=%s', (uid,))
		group_id = cr.fetchone()[0]
		group_obj = self.pool.get('res.groups').browse(cr, uid, group_id, context=context)
		if group_obj.name == 'Financial Manager':
			return True
		else:
			return False
	
	_defaults = {
		'mass_sal_souscr' : 0,
		'state' : 'draft',
		'mod_paiem' : 'cheque',
		'affiche' : _get_group,
	}
	
	def button2_to_sent(self, cr, uid, ids, context=None):
		"""L utilisateur envoi la requete a la comptabilite pour ajouter les informations comptable"""
		# souscripteur = self.pool.get('mcisogem.souscripteur').browse(cr, uid, uid, context=context)
		# usr = self.pool.get('res.users').browse(cr, uid, uid, context=context)
		message = 'Un souscripteur a ete créer veuillez renseigner les informations comptable'
		
		cr.execute('select id from res_groups where name=%s', ('Settings',))
		group_id = cr.fetchone()[0]
		cr.execute('select code_gest_id from res_users where id=%s', (uid,))
		ident_centre = cr.fetchone()[0]
		res_users = self.pool('res.users')
		user_ids = res_users.search(
			cr, SUPERUSER_ID, [
				('code_gest_id', '=', ident_centre),
				('groups_id', 'in', group_id)
			], context=context)     
		partner_id = []
		
		if user_ids:
			partner = self.pool.get('res.partner').browse(cr, uid, uid, context=context) 
			partner_id = list(set(u.partner_id.id for u in res_users.browse(cr, SUPERUSER_ID, user_ids, context=context)))
			partner.message_post(cr, uid, False,
								 body=message,
								 partner_ids=partner_id,
								 subtype='mail.mt_comment', context=context
			)            
		return self.write(cr, uid, ids, {'state':'done'}, context=context)
	
	def button2_to_done(self, cr, uid, ids, context=None):
		"""La comptabilite renseigne et valide les informations comptable"""
		compta = self.read(cr, uid, ids, ['banque_id', 'num_guichet', 'num_compte', \
						'num_compte_interne', 'cle_rib'])        
		if not compta['banque_id'] or not compta['num_guichet'] or not compta['num_compte'] or not compta['num_compte_interne'] or not compta['cle_rib']:
			raise osv.except_osv('Attention !', "Vous devez renseigner tous les champs comptable avant de valider!")
			return False;
		self.write(cr, uid, ids, {'state':'finish'}, context=context)
		return True
	
	def button2_to_cancel(self, cr, uid, ids, context=None):
		self.write(cr, uid, ids, {'state':'done'}, context=context)
		return True 
	
	def create(self, cr, uid, vals, context=None):
		vals['state'] = 'done'
		# vals['name'] = str(vals['name']).upper()


		msg = str("Un nouveau souscripteur vient d'être créé. Vous devez renseigner ses informations comptables.")

		cr.execute("select id from res_groups where name='RESPONSABLE COMPTABLE' or name='UTILISATEUR COMPTABLE'")
		groupe_ids = cr.dictfetchall()

		for groupe_id in groupe_ids:

			groupe_id = groupe_id['id']
			cr.execute('select uid from res_groups_users_rel  where gid=%s', (groupe_id,))
			user_ids = cr.fetchall()

			les_ids = []
			for u_id in user_ids:
				les_ids.append(u_id[0])

			res_users = self.pool['res.users']
			partner_ids = list(set(u.partner_id.id for u in res_users.browse(cr, uid, les_ids , context)))

			self.message_post(
				cr, uid, False,
				body=msg ,
				partner_ids=partner_ids,
				subtype='mail.mt_comment',
				subject="[ISA-WEB] - Validation Comptable",
				context=context
				)



		return super(mcisogem_souscripteur, self).create(cr, uid, vals, context)   

	def write(self, cr, uid, ids, vals, context=None):
		if "banque_id" in vals or "mod_paiem" in vals or "num_compte" in vals or "num_guichet" in vals or "num_compte_interne" in vals or "cle_rib" in vals or "mass_sal_souscr" in vals:

			vals['state'] = 'finish'

		return super(mcisogem_souscripteur, self).write(cr, uid, ids, vals, context=context)
	


