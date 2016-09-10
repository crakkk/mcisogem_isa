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

class mcisogem_agr_prestat(osv.osv):
	_name = "mcisogem.agr.prestat"
	_description = "Rattachement centre medecin"

	_columns = {
		'centre_ids':fields.many2many('mcisogem.centre', 'centre_prestat_rel', 'praticien_rel_id', 'libelle_court_prestat', 'Centres', required=True),
		'code_centre': fields.many2one('mcisogem.centre', 'Centre', required=False, ondelete='CASCADE'),
		'dt_agr_prestat': fields.date('Date d\'agrément', required=True),
		'dt_retr_prestat': fields.date('Date de résiliation'),
		'motif_retr_prestat' : fields.char('Motif du retrait', size=30),
		'praticien_ids':fields.many2many('mcisogem.praticien', 'praticien_rel', 'praticien_rel_id', 'libelle_court_prestat', 'des praticiens', required=True),
	}

	_defaults = {
		'dt_retr_prestat': '1900-01-01'
	}

	_rec_name = 'code_centre'
	 
	
	def create(self, cr, uid, data, context=None):

		centres = data['centre_ids'][0][2]


		for centre in centres:

			deja_rt = self.pool.get('mcisogem.agr.prestat').search(cr,uid,[('code_centre' , '=' , centre)])
			
			if deja_rt:
				raise osv.except_osv('Attention' , 'Un ou plusieurs centres ont déjà été rattachés à des medecins')

			data['code_centre'] = centre
			last_id = super(mcisogem_agr_prestat, self).create(cr, uid, data, context=context)

		return last_id
