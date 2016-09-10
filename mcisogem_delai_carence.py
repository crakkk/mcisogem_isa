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


class mcisogem_libelle_delai(osv.osv):
	_name = "mcisogem.libelle.delai"
	_description = 'Delai'
	
	_columns = {
		'name':fields.char('Delai', required=True),   
	}



class mcisogem_delai_carence_details(osv.osv):
	_name = "mcisogem.delai.carence.details"
	_description = 'Delai details'
	
	_columns = {
		'acte_id':fields.many2one('mcisogem.nomen.prest', 'Acte'),
		'delai':fields.integer('Delai'),
	}


class mcisogem_delai_carence_details_temp(osv.osv):
	_name = "mcisogem.delai.carence.details.temp"
	_description = 'Delai details Temp'
	
	_columns = {
		'acte_id':fields.many2one('mcisogem.nomen.prest', 'Acte'),
		'delai':fields.integer('Delai'),
		'delai_id' : fields.many2one('mcisogem.delai.carence'),
	}


# medicament temp
class mcisogem_delai_carence_medicament_temp(osv.osv):
	_name = "mcisogem.delai.carence.medicament.temp"

	_inherit = "mcisogem.medicament"

	_description = 'Delai medicament Temp'
	
	_columns = {
		'medicament_id':fields.many2one('mcisogem.medicament' , 'Médicament'),
	}



# sous acte temp
class mcisogem_delai_carence_sous_acte_temp(osv.osv):
	_name = "mcisogem.delai.carence.sous.acte.temp"

	_inherit = "mcisogem.sous.actes"

	_description = 'Delai Sous Acte Temp'
	
	_columns = {
		'sous_acte_id':fields.many2one('mcisogem.sous.actes' , 'Sous acte'),
	}


class mcisogem_delai_carence(osv.osv):

	_name = "mcisogem.delai.carence"

	_description = 'Delai de carence'
	
	_columns = {
		'type_delai': fields.selection([('fam', 'Famille d\'actes'),('ss', 'Sous actes'), ('aff', 'Affection'),  ('med', 'Médicaments') ], 'Définir par' , required=True),

		'chargement' : fields.char(''),

		'produit_id':fields.many2one('mcisogem.produit', 'Produit' ,  required=True),

		'fam_acte_ids' : fields.many2many('mcisogem.fam.prest' , 'mcisogem_delai_fam_prest_rel' , 'delai_id' , 'fam_acte_id' , 'Famille d\'actes'),

		'fam_acte_id' : fields.many2one('mcisogem.fam.prest' , 'Famille d\'acte'),



		'aff_ids' : fields.many2many('mcisogem.affec' , 'mcisogem_delai_aff_rel' , 'delai_id' , 'aff_id' , 'Affections'),
		'aff_id' : fields.many2one('mcisogem.affec' , 'Affection'),


		'acte_ids' : fields.many2many('mcisogem.nomen.prest' , 'mcisogem_delai_acte_rel' , 'delai_id' , 'aff_id' , 'Actes'),



		'medicament_ids' : fields.many2many('mcisogem.delai.carence.medicament.temp' , 'mcisogem_delai_medicament_rel' , 'delai_id' , 'medicament_id' , 'Médicaments'),

		# 'medicament_ids' : fields.many2many('mcisogem.medicament' , 'mcisogem_delai_medicament_rel' , 'delai_id' , 'medicament_id' , 'Médicaments'),
		'medicament_id' : fields.many2one('mcisogem.medicament' , 'Médicament'),




		'sous_acte_ids' : fields.many2many('mcisogem.delai.carence.sous.acte.temp' , 'mcisogem_delai_sous_acte_rel' , 'delai_id' , 'sous_acte_id' , 'Sous actes'),

		'sous_acte_id' : fields.many2one('mcisogem.sous.actes' , 'Sous acte'),



		'delai' : fields.integer('Delai (en Jrs)') ,


	}



	# def default_get(self,cr,uid,fields,context=None):
	# 	res = super(mcisogem_delai_carence, self).default_get(cr, uid, fields, context=context)

	# 	les_actes = self.pool.get('mcisogem.nomen.prest').search(cr,uid,[])
	# 	res["acte_ids"] = [(6,0,[les_actes])]
	# 	return res


	_defaults = {
		'chargement' : '1',
	}

	_rec_name = 'produit_id'


	def onchange_type(self,cr,uid,ids,type_delai,context=None):
		if type_delai == 'med':
			f_id = self.pool.get('mcisogem.fam.prest').search(cr,uid,[('libelle_court_famille' , '=' , 'PHAR')])

			if not f_id:
				f_id = self.pool.get('mcisogem.fam.prest').search(cr,uid,[('libelle_court_famille' , '=' , 'FAR')])

				if not f_id:
					f_id = self.pool.get('mcisogem.fam.prest').search(cr,uid,[('libelle_court_famille' , '=' , 'PH')])
			

			if f_id:

				acte_ids = self.pool.get('mcisogem.nomen.prest').search(cr,uid,[('code_fam_prest' , '=' , f_id)])


			return {'domain' : {'acte_ids' : [('id' , 'in' , acte_ids)] } }

		else:
			acte_ids = self.pool.get('mcisogem.nomen.prest').search(cr,uid,[])
			return {'domain' : {'acte_ids' : [('id' , 'in' , acte_ids)] } }

	def onchange_acte(self, cr, uid, ids,acte_ids,type_delai,context=None):


		if type_delai == 'med':

			les_actes = []
			les_medicaments =[]

			cr.execute("delete from mcisogem_delai_carence_medicament_temp where write_uid=%s", (uid,))

			for a_id in acte_ids[0][2]:
				les_actes.append(a_id)


			# les_medicaments = self.pool.get('mcisogem.medicament').search(cr,uid,[('acte_id' , 'in' , les_actes)])

			
			if len(les_actes) > 0:

				for a in les_actes:

					# Recuperation de la liste des actes appartenant à la famille sélectionnée
					cr.execute("select * from mcisogem_medicament where acte_id =%s", (a,))

					lesmed = cr.dictfetchall()

					# Parcours des actes et insertion dans la table temporaire
					for med in lesmed:
						data = {}
						data = med
						data['medicament_id'] = med['id']


						self.pool.get('mcisogem.delai.carence.medicament.temp').create(cr,uid,data)

					
					# Recuperation des actes temporaires enregistré en base
					cr. execute("select * from mcisogem_delai_carence_medicament_temp where write_uid=%s", (uid,))
					les_medicament = cr.dictfetchall()
					print('*******  les_medicaments  ****')
					print(les_medicaments)


					for med in les_medicament:
						les_medicaments.append(med['id'])


			
				return {'value' : {'medicament_ids' : les_medicaments }}

			else:
				return {'value' : {'medicament_ids' : None }}

		elif type_delai == 'ss':
			les_actes = []
			les_s_actes =[]

			cr.execute("delete from mcisogem_delai_carence_sous_acte_temp where write_uid=%s", (uid,))

			for a_id in acte_ids[0][2]:
				les_actes.append(a_id)


			# les_medicaments = self.pool.get('mcisogem.medicament').search(cr,uid,[('acte_id' , 'in' , les_actes)])

			
			if len(les_actes) > 0:

				for a in les_actes:

					# Recuperation de la liste des actes appartenant à la famille sélectionnée
					cr.execute("select * from mcisogem_sous_actes where code_acte =%s", (a,))

					lesss = cr.dictfetchall()

					# Parcours des actes et insertion dans la table temporaire
					for ss in lesss:
						data = {}
						data = ss
						data['sous_acte_id'] = ss['id']


						self.pool.get('mcisogem.delai.carence.sous.acte.temp').create(cr,uid,data)

					
					# Recuperation des actes temporaires enregistré en base
					cr.execute("select * from mcisogem_delai_carence_sous_acte_temp where write_uid=%s", (uid,))
					les_ss = cr.dictfetchall()

					print('*******  les sous actes  ****')
					print(les_ss)


					for ss in les_ss:
						les_s_actes.append(ss['id'])


			
				return {'value' : {'sous_acte_ids' : les_s_actes }}

			else:
				return {'value' : {'sous_acte_ids' : None }}



	def au_chargement(self, cr, uid, ids, chargement, context=None):


		actes = {}
		cr.execute('delete from mcisogem_delai_carence_details_temp where create_uid = %s' , (uid , ))

		les_actes = self.pool.get('mcisogem.nomen.prest').search(cr,uid,[])

		for acte in self.pool.get('mcisogem.nomen.prest').browse(cr,uid,les_actes):
			self.pool.get('mcisogem.delai.carence.details.temp').create(cr,uid,{'acte_id' : acte.id , 'delai' : 0})

		les_delai = self.pool.get('mcisogem.delai.carence.details.temp').search(cr,uid,[])
		
		return {'value' : {'acte_ids' : les_delai}}

		# for acte in self.pool.get('mcisogem.nomen.prest').browse(cr,uid,les_actes):
			
		# 	cr.execute('insert into mcisogem_delai_carence_details_temp(acte_id , delai , create_uid) values(%s , %s , %s)' , (acte.id , 0 , uid , ))
		

	def create(self, cr, uid, vals, context=None):

		if vals['type_delai'] == 'fam':

			if len(vals['fam_acte_ids'][0][2]) == 0:
				osv.except_osv('Attention' , "Vous n'avez sélectionné aucune famille d'acte !")

			for fam in vals['fam_acte_ids'][0][2]:
				vals['fam_acte_id'] = fam


				if self.pool.get('mcisogem.delai.carence').search_count(cr,uid,[('produit_id' , '=' , vals['produit_id']) , ('fam_acte_id' , '=' , vals['fam_acte_id'])]) == 0:

					last_id =  super(mcisogem_delai_carence, self).create(cr, uid, vals, context=context)

				else:
					raise osv.except_osv('Attention' , "L'un des éléments que vous tentez d'enregistrer existe déjà !")




		if vals['type_delai'] == 'aff':

			if len(vals['aff_ids'][0][2]) == 0:
				osv.except_osv('Attention' , "Vous n'avez sélectionné aucune affection !")

			for aff in vals['aff_ids'][0][2]:
				vals['aff_id'] = aff


				if self.pool.get('mcisogem.delai.carence').search_count(cr,uid,[('produit_id' , '=' , vals['produit_id']) , ('aff_id' , '=' , vals['aff_id'])]) == 0:

					last_id =  super(mcisogem_delai_carence, self).create(cr, uid, vals, context=context)

				else:
					raise osv.except_osv('Attention' , "L'un des éléments que vous tentez d'enregistrer existe déjà !")

		if vals['type_delai'] == 'ss':
			if len(vals['sous_acte_ids'][0][2]) == 0:
				osv.except_osv('Attention' , "Vous n'avez sélectionné aucun sous acte !")

			for ss in vals['sous_acte_ids'][0][2]:
				s_acte = self.pool.get('mcisogem.delai.carence.sous.acte.temp').browse(cr,uid,ss)

				vals['sous_acte_id'] = s_acte.sous_acte_id.id
				vals['medicament_ids'] = None
				vals['sous_acte_ids'] = None

				if self.pool.get('mcisogem.delai.carence').search_count(cr,uid,[('produit_id' , '=' , vals['produit_id']) , ('sous_acte_id' , '=' , vals['sous_acte_id'])]) == 0:

					last_id =  super(mcisogem_delai_carence, self).create(cr, uid, vals, context=context)

				else:
					raise osv.except_osv('Attention' , "L'un des éléments que vous tentez d'enregistrer existe déjà !")


		if vals['type_delai'] == 'med':

			if len(vals['medicament_ids'][0][2]) == 0:
				osv.except_osv('Attention' , "Vous n'avez sélectionné aucun médicament !")

			for med in vals['medicament_ids'][0][2]:
				medicament = self.pool.get('mcisogem.delai.carence.medicament.temp').browse(cr,uid,med)
				vals['medicament_ids'] = None
				vals['sous_acte_ids'] = None
				vals['medicament_id'] = medicament.medicament_id.id

				if self.pool.get('mcisogem.delai.carence').search_count(cr,uid,[('produit_id' , '=' , vals['produit_id']) , ('medicament_id' , '=' , vals['medicament_id'])]) == 0:

					last_id =  super(mcisogem_delai_carence, self).create(cr, uid, vals, context=context)

				else:
					raise osv.except_osv('Attention' , "L'un des éléments que vous tentez d'enregistrer existe déjà !")


		return last_id





# class mcisogem_delai_carence(osv.osv):
# 	_name = "mcisogem.delai.carence"
# 	_description = 'Delai de Carence'
	


# 	def _get_context(self, cr, uid, context):
# 		context = context or {}
# 		return context.get('police')



# 	_columns = {
# 		'police_id' : fields.many2one('mcisogem.police' , 'Police'),

# 		'affiche_par' :fields.selection([ ('fam', 'Famille d\'actes') ,('acte', 'Acte'),('aff', 'Affection') ], 'Affiché par', required=True),

# 		'fam_acte_ids':fields.many2many('mcisogem.fam.prest',
# 									    'mcisogem_delai_fam_prest_rel',
# 										'fam_acte_1',
# 										'fam_ac2e_1', 'Famille d\'actes', required=False),


# 		'cod_statut_ids':fields.many2many('mcisogem.stat.benef',
# 									    'mcisogem_delai_stat_benef_rel',
# 										'cod_statut_benef_1',
# 										'cod_statut_benef', 'Statuts', required=False),

		
# 		'cod_tranche_age_ids':fields.many2many('mcisogem.tranche.age',
# 									   'mcisogem_delai_age_rel',
# 										'tranche_age_id',
# 										'tranche_age', 'Tranches d\'age', required=False),
				

# 		'cod_acte_ids':fields.many2many('mcisogem.nomen.prest',
# 									    'mcisogem_delai_acte_rel',
# 										'acte_id',
# 										'code_acte', 'Actes', required=False),

# 		'cod_affec_ids':fields.many2many('mcisogem.affec',
# 									    'mcisogem_delai_affec_rel',
# 										'affec_id',
# 										'cod_affec', 'Affections', required=False),

# 		'cod_col_ids':fields.many2many('mcisogem.college',
# 									    'mcisogem_delai_college_rel',
# 										'col_id',
# 										'col_id_2', 'Collèges', required=False),


# 		'fam_acte_id' : fields.many2one('mcisogem.fam.prest' , 'Famille'),
# 		'code_statut_id' : fields.many2one('mcisogem.stat.benef' , 'Statut'),
# 		'code_tranche_age_id' : fields.many2one('mcisogem.tranche.age' , 'Tranche d\' age'),
# 		'code_acte_id' : fields.many2one('mcisogem.nomen.prest' , 'Acte'),
# 		'code_affec_id' : fields.many2one('mcisogem.affec' , 'Affection'),
# 		'cod_col_id' : fields.many2one('mcisogem.college' , 'Collège'),

# 		'nbre_mois' : fields.integer('Nombre de Jours' , required=True) , 
		 
# 		'type_prime' : fields.integer('')


# 	}
	

# 	_defaults = {
# 		'police_id' : _get_context
# 	}

# 	_rec_name = 'cod_col_id'


# 	def onchange_police(self, cr, uid, ids, name, context=None):
# 		if not name:
# 			return {'value': {'police_id': False}}
# 		else:
# 			obj_police_data = self.pool.get('mcisogem.police').browse(cr, uid, name, context=context)
# 			v= {}

# 			v['type_prime'] = int(obj_police_data.type_prime)

# 			return {'value' : v}

# 	def create(self, cr, uid, vals, context=None):
# 		vals['police_id'] = self._get_context(cr,uid,context)
# 		vals['type_prime'] = self.onchange_police(cr,uid,1,vals['police_id'])['value']['type_prime']

# 		les_familles_acte = vals['fam_acte_ids']
# 		les_actes = vals['cod_acte_ids']
# 		les_affections = vals['cod_affec_ids']
# 		les_statuts  = vals['cod_statut_ids']
# 		les_tranches = vals['cod_tranche_age_ids']
# 		les_colleges = vals['cod_col_ids']
# 		affiche_par = vals['affiche_par']
# 		type_prime = int(self.onchange_police(cr,uid,1,vals['police_id'])['value']['type_prime'])

		
# 		data = {}

# 		if affiche_par == 'acte':
# 			for col in les_colleges[0][2]:
# 				for acte in les_actes[0][2]:

# 					if self.onchange_police(cr,uid,1,vals['police_id'])['value']['type_prime'] == 1:
# 						# prime par statut

# 						for statut in les_statuts[0][2]:

# 							data['type_prime'] = type_prime
# 							data['cod_col_id'] = col
# 							data['police_id'] = vals['police_id']
# 							data['code_acte_id'] = acte
# 							data['code_statut_id'] =  statut
# 							data['nbre_mois'] = vals['nbre_mois']
# 							data['affiche_par'] = affiche_par

# 							dernier_id = super(mcisogem_delai_carence, self).create(cr, uid, data, context=context)

# 							# cr.execute("insert into mcisogem_delai_carence(type_prime , cod_col_id , police_id , code_acte_id , code_statut_id , nbre_mois , affiche_par) values(%s , %s ,%s , %s, %s , %s , %s)" , (type_prime , col , vals['police_id'] , acte , statut , vals['nbre_mois'] , affiche_par))

# 					else:
# 						# prime par tranche age

# 						for tranche in les_tranches[0][2]:

# 							data['type_prime'] = type_prime
# 							data['cod_col_id'] = col
# 							data['police_id'] = vals['police_id']
# 							data['code_acte_id'] = acte
# 							data['code_tranche_age_id'] =  tranche
# 							data['nbre_mois'] = vals['nbre_mois']
# 							data['affiche_par'] = affiche_par

# 							dernier_id = super(mcisogem_delai_carence, self).create(cr, uid, data, context=context)

# 							# cr.execute("insert into mcisogem_delai_carence(type_prime , cod_col_id , police_id , code_acte_id , code_tranche_age_id , nbre_mois , affiche_par) values(%s , %s , %s ,%s, %s, %s , %s)" , (type_prime , col , vals['police_id'] , acte , tranche , vals['nbre_mois'] , affiche_par))
		

				
# 		if affiche_par == 'fam':
# 			for col in les_colleges[0][2]:
# 				for fam in les_familles_acte[0][2]:

# 					if self.onchange_police(cr,uid,1,vals['police_id'])['value']['type_prime'] == 1:
# 						# prime par statut

						
# 						for statut in les_statuts[0][2]:

# 							data['type_prime'] = type_prime
# 							data['cod_col_id'] = col
# 							data['police_id'] = vals['police_id']
# 							data['fam_acte_id'] = fam
# 							data['code_statut_id'] =  statut
# 							data['nbre_mois'] = vals['nbre_mois']
# 							data['affiche_par'] = affiche_par

# 							dernier_id = super(mcisogem_delai_carence, self).create(cr, uid, data, context=context)


# 							# cr.execute("insert into mcisogem_delai_carence(type_prime , cod_col_id , police_id , fam_acte_id , code_statut_id , nbre_mois , affiche_par) values(%s , %s ,%s , %s, %s , %s , %s)" , (type_prime , col , vals['police_id'] , fam , statut , vals['nbre_mois'] , affiche_par))

# 					else:
# 						# prime par tranche age

# 						for tranche in les_tranches[0][2]:

# 							data['type_prime'] = type_prime
# 							data['cod_col_id'] = col
# 							data['police_id'] = vals['police_id']
# 							data['fam_acte_id'] = fam
# 							data['code_tranche_age_id'] =  tranche
# 							data['nbre_mois'] = vals['nbre_mois']
# 							data['affiche_par'] = affiche_par

# 							dernier_id = super(mcisogem_delai_carence, self).create(cr, uid, data, context=context)


# 							# cr.execute("insert into mcisogem_delai_carence(type_prime  ,cod_col_id , police_id , fam_acte_id , code_tranche_age_id , nbre_mois , affiche_par) values(%s , %s ,%s, %s, %s, %s , %s , %S)" , (type_prime , col , vals['police_id'] , fam , tranche , vals['nbre_mois']  , affiche_par))

# 		if affiche_par == 'aff':
# 			for col in les_colleges[0][2]:
# 				for aff in les_affections[0][2]:

# 					if self.onchange_police(cr,uid,1,vals['police_id'])['value']['type_prime'] == 1:
# 						# prime par statut


# 						for statut in les_statuts[0][2]:

# 							data['type_prime'] = type_prime
# 							data['cod_col_id'] = col
# 							data['police_id'] = vals['police_id']
# 							data['code_affec_id'] = aff
# 							data['code_statut_id'] =  statut
# 							data['nbre_mois'] = vals['nbre_mois']
# 							data['affiche_par'] = affiche_par

# 							dernier_id = super(mcisogem_delai_carence, self).create(cr, uid, data, context=context)


# 							# cr.execute("insert into mcisogem_delai_carence(type_prime , cod_col_id , police_id , code_affec_id , code_statut_id , nbre_mois , affiche_par) values(%s , %s ,%s, %s , %s , %s , %s)" , (type_prime , col , vals['police_id'] , aff , statut , vals['nbre_mois'] , affiche_par))

# 					else:
# 						# prime par tranche age

# 						for tranche in les_tranches[0][2]:

# 							data['type_prime'] = type_prime
# 							data['cod_col_id'] = col
# 							data['police_id'] = vals['police_id']
# 							data['code_affec_id'] = aff
# 							data['code_tranche_age_id'] =  tranche
# 							data['nbre_mois'] = vals['nbre_mois']
# 							data['affiche_par'] = affiche_par

# 							dernier_id = super(mcisogem_delai_carence, self).create(cr, uid, data, context=context)


# 							cr.execute("insert into mcisogem_delai_carence(type_prime , cod_col_id , police_id , code_affec_id , code_tranche_age_id , nbre_mois , affiche_par) values(%s , %s ,%s, %s, %s , %s , %s)" , (type_prime , col , vals['police_id'] , aff , tranche , vals['nbre_mois'] , affiche_par))


				
# 		return dernier_id
		

