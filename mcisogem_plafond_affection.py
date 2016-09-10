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




class mcisogem_affection_plafond_temp(osv.osv):
	_name = "mcisogem.affection.plafond.temp"
	_description = 'Delai details'
	
	_columns = {
		'affec_id':fields.many2one('mcisogem.affec', 'Affection'),
		'plafond':fields.integer('plafond'),
	}




class mcisogem_plafond_affection(osv.osv):
	_name = "mcisogem.plafond.affection"
	_description = 'Exclusion Affection'


	_columns = {
		

		'tout_benef' : fields.boolean('Tous les bénéficiaires'),

		'chapitre_affec_ids':fields.many2many('mcisogem.chapitre.affection',
										'mcisogem_exclusion_aff_chapitre',
										'plf_id',
										'chap_aff_id', '', required=False),

		'sous_chap_affec_ids':fields.many2many('mcisogem.sous.chapitre.affection',
										'mcisogem_exclusion_aff_s_chapitre',
										'plf_id',
										's_chap_aff_id', '', required=False),

		'plafond':fields.integer('plafond' , required=True),

		'affec_ids':fields.many2many('mcisogem.affec',
										'mcisogem_aff_plfd_rel',
										'plf_id',
										'aff_id', 'Affections', required=False),



		'cod_benef_ids':fields.many2many('mcisogem.benef',
										'mcisogem_plafond_acte_benef__rel',
										'plf_id',
										'benef_id', 'bénéficiaires', required=False),


		'police_ids':fields.many2many('mcisogem.police',
										'mcisogem_plafond_affec_police_rel',
										'plf_id',
										'police_id', 'Polices', required=False),


		'college_ids':fields.many2many('mcisogem.college',
										'mcisogem_plafond_affec_college_rel',
										'plf_id',
										'col_id', 'Collèges', required=False),

		'dt_effet': fields.date('Date d\'effet', required=True),

		'code_aff_id' : fields.many2one('mcisogem.affec' , 'Affection'),


		'benef_id' : fields.many2one('mcisogem.benef' , 'Bénéficiaire'),
	}

	_defaults = {
		'tout_benef' : True,
		'dt_effet': time.strftime("%Y-%m-%d", time.localtime()),
	}

	_rec_name = "code_aff_id"



	def onchange_chapitre(self, cr, uid, ids,chapitre_ids, context=None):
		d = {}
		
		if chapitre_ids[0][2]:

			cr.execute('delete from mcisogem_affection_plafond_temp where create_uid = %s' , (uid  , ))
			

			chapitre_ids = chapitre_ids[0][2]

			s_chap_ids = self.pool.get('mcisogem.sous.chapitre.affection').search(cr,uid,[('chapitre_id' , 'in' , chapitre_ids)])

			les_affec = self.pool.get('mcisogem.affec').search(cr,uid,[('sous_chapitre_id' , 'in' , s_chap_ids)])

			return {'domain' : {'sous_chap_affec_ids' : [('id' , 'in' , s_chap_ids)] , 'affec_ids' : [('id' , 'in' , les_affec)]}}


	def onchange_sous_chapitre(self, cr, uid, ids,s_chap_ids, context=None):
		d = {}
		
		if s_chap_ids[0][2]:

			cr.execute('delete from mcisogem_affection_plafond_temp where create_uid = %s' , (uid , ))

			s_chap_ids = s_chap_ids[0][2]

			les_affec = self.pool.get('mcisogem.affec').search(cr,uid,[('sous_chapitre_id' , 'in' , s_chap_ids)])

			return {'domain' : {'affec_ids' : [('id' , 'in' , les_affec)]}}



	def onchange_police(self, cr, uid, ids,police_ids, context=None):
		d = {}
		
		if police_ids[0][2]:
			police_ids = police_ids[0][2]

			les_benefs = self.pool.get('mcisogem.benef').search(cr,uid,[('police_id' , 'in' , police_ids)])

			les_colleges = self.pool.get('mcisogem.college').search(cr,uid,[('police_id' , 'in' , police_ids)])

			return {'domain' : {'college_ids' : [('id' , 'in' , les_colleges)] , 'cod_benef_ids' : [('id' , 'in' , les_benefs)]}}

	
	def onchange_college(self, cr, uid, ids,college_ids, context=None):
		d = {}
		
		if college_ids[0][2]:
			college_ids = college_ids[0][2]

			les_benefs = self.pool.get('mcisogem.benef').search(cr,uid,[('college_id' , 'in' , college_ids)])

			return {'domain' : {'cod_benef_ids' : [('id' , 'in' , les_benefs)]}}







	def create(self, cr, uid, vals, context=None):

		dernier_id = False

		affec_ids = vals['affec_ids'][0][2]
		
		if len(affec_ids) == 0:
			raise osv.except_osv('Attention !' , "Aucune affection n'a été selectionnée.")

		if vals['tout_benef']:

			for af in affec_ids:

				sch = self.pool.get('mcisogem.plafond.affection').search(cr,uid,[('code_aff_id' , '=' , af) , ('tout_benef' , '=' , True)])
				
				if sch:
					raise osv.except_osv('Attention !' , 'Un plafond a déjà été défini pour cette affection.')

				vals['code_aff_id'] = af

				dernier_id = super(mcisogem_plafond_affection, self).create(cr, uid, vals, context=context)

		else:

			for af in affec_ids:


				vals['code_aff_id'] = af

				cod_benef_ids = vals['cod_benef_ids'][0][2]

				if len(cod_benef_ids) == 0:
					raise osv.except_osv('Attention !' , "Aucun bénéficiaire n'a été selectionné.")


				for bn in cod_benef_ids:

					sch = self.pool.get('mcisogem.plafond.affection').search(cr,uid,[('code_aff_id' , '=' , af) , ('benef_id' , '=' , bn)])
				
					if sch:
						raise osv.except_osv('Attention !' , 'Un plafond pour la même affection et pour ce bénéficiaire a déjà été défini.')


					vals['benef_id'] = bn

					dernier_id = super(mcisogem_plafond_affection, self).create(cr, uid, vals, context=context)

		return dernier_id








