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


class mcisogem_surprime(osv.osv):
	_name = "mcisogem.surprime"
	_description = "Surprime"



	def _get_benef(self, cr,uid,context):
		if context.get('benef_id'):
			return context.get('police')
		else:
			return False


	def onchange_benef(self, cr, uid, ids, benef_id, context=None):
		if not benef_id:
			return False
		else:

			d ={}
			benef = self.pool.get('mcisogem.benef').search(cr, uid, [('id', '=', benef_id)])
			b_data = self.pool.get('mcisogem.benef').browse(cr, uid, benef)
			
			polices = []

			if benef_id:
				police_id = self.pool.get('mcisogem.benef').browse(cr,uid,benef_id).police_id
				polices.append(police_id.id)

				p = self.pool.get('mcisogem.police.complementaire.beneficiaire').search(cr,uid,[('beneficiaire_id' , '=' , benef_id)] ,order='niveau ASC')

				if p:
					for police_id in self.pool.get('mcisogem.police.complementaire.beneficiaire').browse(cr,uid,p):

						polices.append(police_id.police_id.id)

			d = {'police_id':[('id' , 'in', polices)]}			

		return {'domain':d}

	_columns = {
		'benef_id' : fields.many2one('mcisogem.benef' , 'Beneficiaire' , required=True , readonly=True),
		# 'garant_id': fields.many2one('mcisogem.garant', 'Assureur', required=True ),
		'police_id' : fields.many2one('mcisogem.police' , 'Police'),
		'college_id' : fields.many2one('mcisogem.college', 'College'),
		'type_surprime_sans_sida' : fields.boolean('Montant en %'),
		'sur_prime_sans_sida' :fields.integer('Surprime sans sida'),
		'type_surprime_sida' : fields.boolean('Montant en %'),
		'sur_prime_sida' : fields.integer('Surprime sida'),
		'affiche' : fields.boolean(''),
	}

	_defaults ={
		'affiche' : True , 
		'benef_id' : _get_benef
	}

	_rec_name = "benef_id" 


	# def create(self, cr, uid, vals, context=None):

	# 	vals['benef_id'] = context.get('police')

	# 	if vals['type_surprime_sans_sida']:
	# 		if vals['sur_prime_sans_sida'] > 100:
	# 			raise osv.except_osv('Attention !', "La Valeur en '%' ne peut excéder 100 !")


	# 	if vals['type_surprime_sida']:
	# 		if vals['sur_prime_sida'] > 100:
	# 			raise osv.except_osv('Attention !', "La Valeur en '%' ne peut excéder 100 !")


	# 	if vals['police_temp_id'] and vals['college_temp_id']:
	# 		vals['affiche'] = False

	# 		police_search = self.pool.get('mcisogem.police.benef.temp').search(cr,uid,[('id', '=', vals['police_temp_id'])])
	# 		police = self.pool.get('mcisogem.police.benef.temp').browse(cr,uid,police_search)
	# 		vals['police_id'] = police.police_id.id


	# 		college_search = self.pool.get('mcisogem.college.police.temp').search(cr,uid,[('id', '=', vals['college_temp_id'])])
	# 		college = self.pool.get('mcisogem.college.police.temp').browse(cr,uid,college_search)
	# 		vals['college_id'] = college.college_id.id


	# 		res = super(mcisogem_surprime, self).create(cr, uid, vals, context=context)
	# 		cr.execute('delete from mcisogem_police_benef_temp where create_uid = %s' , (uid , ))
	# 		cr.execute('delete from mcisogem_college_police_temp where create_uid = %s' , (uid , ))
	# 		return res

	# 	else:
	# 		raise osv.except_osv('Attention !', "Veuillez choisir une police et un collège !")




class mcisogem_police_benef_temp(osv.osv):
	_name = "mcisogem.police.benef.temp"
	_description = "Polices du bénéficiaire"


	_columns = {
		'police_id' : fields.many2one('mcisogem.police' , 'Police'),
		'benef_id' : fields.many2one('mcisogem.benef' , 'Bénéficiaire'),
	}

	_rec_name = "police_id"



class mcisogem_college_police_temp(osv.osv):
	_name = "mcisogem.college.police.temp"
	_description = "Colleges de la police"


	_columns = {
		'college_id' : fields.many2one('mcisogem.college' , 'College'),
	}

	_rec_name = "college_id"

