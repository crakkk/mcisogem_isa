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


class mcisogem_exclusion_acte(osv.osv):
	_name = "mcisogem.exclusion.acte"
	_description = 'exclusion Acte'


	def _get_context(self, cr, uid, context):
		context = context or {}
		return context.get('police')


	_columns = {
		

		'affiche_par' :fields.selection([ ('fam', 'Famille d\'actes') ,('acte', 'Actes'),('s-acte', 'Sous actes') ,('aff', 'Affections'),  ('med', 'Médicaments')], 'Affiché par', required=True),

		'tout_benef' : fields.boolean('Tous les bénéficiaires'),

		'fam_acte_ids':fields.many2many('mcisogem.fam.prest',
										'mcisogem_exclusion_acte_fam_prest_rel',
										'cod_excl',
										'fam_acte', 'Famille d\'actes', required=False),



		'cod_police_ids':fields.many2many('mcisogem.police',
										'mcisogem_exclusion_acte_police_rel',
										'cod_excl',
										'cod_police', 'Statuts', required=False),


		'cod_statut_ids':fields.many2many('mcisogem.stat.benef',
										'mcisogem_exclusion_acte_stat_benef_rel',
										'cod_excl',
										'cod_statut_benef', 'Statuts', required=False),
				

		'cod_acte_ids':fields.many2many('mcisogem.nomen.prest',
										'mcisogem_exclusion_acte_acte_rel',
										'cod_excl',
										'code_acte', 'Actes', required=False),

		'cod_med_ids':fields.many2many('mcisogem.medicament',
										'mcisogem_exclusion_med_rel',
										'cod_excl',
										'code_med', 'Médicaments', required=False),



		'cod_s_acte_ids':fields.many2many('mcisogem.sous.actes',
										'mcisogem_exclusion_acte_sous_acte_rel',
										'cod_excl',
										'cod_affec', 'Sous actes', required=False),

		'cod_aff_ids':fields.many2many('mcisogem.affec',
										'mcisogem_exclusion_acte_aff_rel',
										'cod_excl',
										'cod_affec', 'Affections', required=False),



		'cod_col_ids':fields.many2many('mcisogem.college',
										'mcisogem_exclusion_acte_college_rel',
										'cod_excl',
										'col_id', 'Collèges', required=False),

		'cod_benef_ids':fields.many2many('mcisogem.benef',
										'mcisogem_exclusion_acte_benef__rel',
										'cod_excl',
										'benef_id', 'bénéficiaires', required=False),

		'police_id' : fields.many2one('mcisogem.police' , 'Police'),

		'fam_acte_id' : fields.many2one('mcisogem.fam.prest' , 'Famille'),

		'code_statut_id' : fields.many2one('mcisogem.stat.benef' , 'Statut'),

		'code_acte_id' : fields.many2one('mcisogem.nomen.prest' , 'Acte'),

		'code_med_id' : fields.many2one('mcisogem.medicament' , 'Médicament'),

		'code_s_acte_id' : fields.many2one('mcisogem.sous.actes' , 'Sous acte'),

		'code_aff_id' : fields.many2one('mcisogem.affec' , 'Affection'),

		
		'cod_col_id' : fields.many2one('mcisogem.college' , 'Collège'),
		'cod_benef_id' : fields.many2one('mcisogem.benef' , 'Bénéficiaire'),
	}

	_rec_name = 'cod_col_id'


	_defaults = {
		'tout_benef' : True,
	}
	def onchange_police(self, cr, uid, ids, police_ids,college_ids,statut_ids, context=None):
		d = {}
		critere = []

		
		if police_ids[0][2]:
			police_ids = police_ids[0][2]
			stat_ids = []
			col_ids = self.pool.get('mcisogem.college').search(cr,uid,[('police_id' , 'in' , police_ids)])
			ben_ids = self.pool.get('mcisogem.benef').search(cr,uid,[('police_id' , 'in' , police_ids)])
			histo_ids = self.pool.get('mcisogem.histo.police').search(cr,uid,[('name' , 'in' ,  police_ids)])

			for h in self.pool.get('mcisogem.histo.police').browse(cr,uid,histo_ids):

				for st in h.statut_ids:
					stat_ids.append(st.id)

			if college_ids[0][2]:
				col_ids = college_ids[0][2]
				ben_ids = self.pool.get('mcisogem.benef').search(cr,uid,[('college_id' , 'in' , col_ids) , ('id' , 'in' , ben_ids)])

				

			if statut_ids[0][2]:
				stat_ids = statut_ids[0][2]
				ben_ids = self.pool.get('mcisogem.benef').search(cr,uid,[('statut_benef' , 'in' , stat_ids) , ('id' , 'in' , ben_ids)])


			critere.append(('id' , 'in' , ben_ids))

			return {'domain' : {'cod_col_ids' : [('id' , 'in' , col_ids)] , 'cod_statut_ids' : [('id' , 'in' , stat_ids)] , 'cod_benef_ids' : critere} }




	def create(self, cr, uid, vals, context=None):

		les_familles_acte = vals['fam_acte_ids']
		les_actes = vals['cod_acte_ids']
		les_s_actes = vals['cod_s_acte_ids']
		les_statuts  = vals['cod_statut_ids']
		les_benefs = vals['cod_benef_ids']
		les_colleges = vals['cod_col_ids']
		les_polices = vals['cod_police_ids']
		les_medicaments = vals['cod_med_ids']
		les_affections = vals['cod_aff_ids']

		affiche_par = vals['affiche_par']

		data = {}
		data['tout_benef'] = vals['tout_benef']


		dernier_id = False
		# on vérifie si tous les champs de base ont été renseignés
		if len(les_polices[0][2]) == 0:
			raise osv.except_osv('Attention' , 'Vous devez sélectionner au moins une police !')

		if len(les_colleges[0][2]) == 0:
			raise osv.except_osv('Attention' , 'Vous devez sélectionner au moins un collège !')


		if vals['tout_benef'] == False:
			if len(les_benefs[0][2]) == 0:
				raise osv.except_osv('Attention' , 'Vous devez sélectionner au moins un bénéficiaire !')

		else:
			if len(les_statuts[0][2]) == 0:
				raise osv.except_osv('Attention' , 'Vous devez sélectionner au moins un statut de bénéficiaire !')

		if affiche_par == 'acte':

			if len(les_actes[0][2]) == 0:
				raise osv.except_osv('Attention' , 'Vous devez sélectionner au moins un acte !')

			for pol in les_polices[0][2]:

				for col in les_colleges[0][2]:

					college_data = self.pool.get('mcisogem.college').browse(cr,uid,col)

					if college_data.police_id.id == pol:


						for acte in les_actes[0][2]:

							if vals['tout_benef'] == False:
								# enregistrement par beneficiaire

								for benef in les_benefs[0][2]:

									data['police_id'] = pol
									data['cod_col_id'] = col
									data['code_acte_id'] = acte
									data['cod_benef_id'] = benef
									data['affiche_par'] = affiche_par

									if self.pool.get('mcisogem.benef').browse(cr,uid,benef).college_id == col:

										srch = self.pool.get('mcisogem.exclusion.acte').search_count(cr,uid,[('police_id' , '=' , pol) , ('cod_col_id' , '=' , col) , ('code_acte_id' , '=' , acte) , ('cod_benef_id' , '=' , benef)])

										if srch == 0:

											dernier_id = super(mcisogem_exclusion_acte, self).create(cr, uid, data, context=context)
							else:
								# enregistrement par statut
								for statut in les_statuts[0][2]:

									data['police_id'] = pol
									data['cod_col_id'] = col
									data['code_acte_id'] = acte
									data['code_statut_id'] =  statut
									data['affiche_par'] = affiche_par

									srch = self.pool.get('mcisogem.exclusion.acte').search_count(cr,uid,[('police_id' , '=' , pol) , ('cod_col_id' , '=' , col) , ('code_acte_id' , '=' , acte) , ('code_statut_id' , '=' , statut)])

									if srch == 0:

										dernier_id = super(mcisogem_exclusion_acte, self).create(cr, uid, data, context=context)

		

				
		if affiche_par == 'fam':

			if len(les_familles_acte[0][2]) == 0:
				raise osv.except_osv('Attention' , 'Vous devez sélectionner au moins une famille d\' acte !')


			for pol in les_polices[0][2]:
				for col in les_colleges[0][2]:

					college_data = self.pool.get('mcisogem.college').browse(cr,uid,col)

					if college_data.police_id.id == pol:

						for fam in les_familles_acte[0][2]:
							
							if vals['tout_benef'] == False:
									# enregistrement par beneficiaire

								for benef in les_benefs[0][2]:

									data['police_id'] = pol
									data['cod_col_id'] = col
									data['fam_acte_id'] = fam
									data['cod_benef_id'] = benef
									data['affiche_par'] = affiche_par

									if self.pool.get('mcisogem.benef').browse(cr,uid,benef).college_id.id == col:

										srch = self.pool.get('mcisogem.exclusion.acte').search_count(cr,uid,[('police_id' , '=' , pol) , ('cod_col_id' , '=' , col) , ('fam_acte_id' , '=' , fam) , ('cod_benef_id' , '=' , benef)])

										if srch == 0:

											dernier_id = super(mcisogem_exclusion_acte, self).create(cr, uid, data, context=context)


							else:
								# enregistrement par statut
								for statut in les_statuts[0][2]:

									data['police_id'] = pol
									data['cod_col_id'] = col
									data['fam_acte_id'] = fam
									data['code_statut_id'] =  statut
									data['affiche_par'] = affiche_par

									srch = self.pool.get('mcisogem.exclusion.acte').search_count(cr,uid,[('police_id' , '=' , pol) , ('cod_col_id' , '=' , col) , ('fam_acte_id' , '=' , fam) , ('code_statut_id' , '=' , statut)])

									if srch == 0:

										dernier_id = super(mcisogem_exclusion_acte, self).create(cr, uid, data, context=context)


		if affiche_par == 's-acte':

			if len(les_s_actes[0][2]) == 0:
				raise osv.except_osv('Attention' , 'Vous devez sélectionner au moins un acte !')


			for pol in les_polices[0][2]:
				for col in les_colleges[0][2]:

					college_data = self.pool.get('mcisogem.college').browse(cr,uid,col)

					if college_data.police_id.id == pol:


						for s_acte in les_s_actes[0][2]:

							if vals['tout_benef'] == False:
									# enregistrement par beneficiaire

								for benef in les_benefs[0][2]:

									data['police_id'] = pol
									data['cod_col_id'] = col
									data['code_s_acte_id'] = s_acte
									data['cod_benef_id'] = benef
									data['affiche_par'] = affiche_par

									if self.pool.get('mcisogem.benef').browse(cr,uid,benef).college_id.id == col:

										srch = self.pool.get('mcisogem.exclusion.acte').search_count(cr,uid,[('police_id' , '=' , pol) , ('cod_col_id' , '=' , col) , ('code_s_acte_id' , '=' , s_acte) , ('cod_benef_id' , '=' , benef)])

										dernier_id = super(mcisogem_exclusion_acte, self).create(cr, uid, data, context=context)
							else:
								# enregistrement par statut
								for statut in les_statuts[0][2]:

									data['police_id'] = pol
									data['cod_col_id'] = col
									data['code_s_acte_id'] = s_acte
									data['code_statut_id'] =  statut
									data['affiche_par'] = affiche_par

									srch = self.pool.get('mcisogem.exclusion.acte').search_count(cr,uid,[('police_id' , '=' , pol) , ('cod_col_id' , '=' , col) , ('code_s_acte_id' , '=' , s_acte) , ('code_statut_id' , '=' , statut)])

									dernier_id = super(mcisogem_exclusion_acte, self).create(cr, uid, data, context=context)


		if affiche_par == 'med':
			if len(les_medicaments[0][2]) == 0:
				raise osv.except_osv('Attention' , 'Vous devez sélectionner au moins un médicament !')


			for pol in les_polices[0][2]:
				for col in les_colleges[0][2]:

					college_data = self.pool.get('mcisogem.college').browse(cr,uid,col)

					if college_data.police_id.id == pol:


						for med in les_medicaments[0][2]:

							if vals['tout_benef'] == False:
								# enregistrement par beneficiaire

								for benef in les_benefs[0][2]:

									data['police_id'] = pol
									data['cod_col_id'] = col
									data['code_med_id'] = med

									data['cod_benef_id'] = benef
									data['affiche_par'] = affiche_par

									if self.pool.get('mcisogem.benef').browse(cr,uid,benef).college_id.id == col:

										srch = self.pool.get('mcisogem.exclusion.acte').search_count(cr,uid,[('police_id' , '=' , pol) , ('cod_col_id' , '=' , col) , ('code_med_id' , '=' , med) , ('cod_benef_id' , '=' , benef)])

										dernier_id = super(mcisogem_exclusion_acte, self).create(cr, uid, data, context=context)
							else:
								# enregistrement par statut
								for statut in les_statuts[0][2]:

									data['police_id'] = pol
									data['cod_col_id'] = col
									data['code_med_id'] = med
									data['code_statut_id'] =  statut
									data['affiche_par'] = affiche_par

									srch = self.pool.get('mcisogem.exclusion.acte').search_count(cr,uid,[('police_id' , '=' , pol) , ('cod_col_id' , '=' , col) , ('code_med_id' , '=' , med) , ('code_statut_id' , '=' , statut)])

									dernier_id = super(mcisogem_exclusion_acte, self).create(cr, uid, data, context=context)




		if affiche_par == 'aff':

			if len(les_affections[0][2]) == 0:
				raise osv.except_osv('Attention' , 'Vous devez sélectionner au moins une affection !')


			for pol in les_polices[0][2]:
				for col in les_colleges[0][2]:

					college_data = self.pool.get('mcisogem.college').browse(cr,uid,col)

					if college_data.police_id.id == pol:


						for aff in les_affections[0][2]:

							if vals['tout_benef'] == False:
									# enregistrement par beneficiaire

								for benef in les_benefs[0][2]:

									data['police_id'] = pol
									data['cod_col_id'] = col
									data['code_aff_id'] = aff
									data['cod_benef_id'] = benef
									data['affiche_par'] = affiche_par

									if self.pool.get('mcisogem.benef').browse(cr,uid,benef).college_id.id == col:

										srch = self.pool.get('mcisogem.exclusion.acte').search_count(cr,uid,[('police_id' , '=' , pol) , ('cod_col_id' , '=' , col) , ('code_aff_id' , '=' , aff) , ('cod_benef_id' , '=' , benef)])

										dernier_id = super(mcisogem_exclusion_acte, self).create(cr, uid, data, context=context)
							else:
								# enregistrement par statut
								for statut in les_statuts[0][2]:

									data['police_id'] = pol
									data['cod_col_id'] = col
									data['code_aff_id'] = aff
									data['code_statut_id'] =  statut
									data['affiche_par'] = affiche_par

									srch = self.pool.get('mcisogem.exclusion.acte').search_count(cr,uid,[('police_id' , '=' , pol) , ('cod_col_id' , '=' , col) , ('code_aff_id' , '=' , aff) , ('code_statut_id' , '=' , statut)])

									dernier_id = super(mcisogem_exclusion_acte, self).create(cr, uid, data, context=context)



		if dernier_id == False:
			raise osv.except_osv('Attention' , 'Les éléments que vous essayez de créer existent déjà ou ne peuvent être crées!')
				
		return dernier_id
		

