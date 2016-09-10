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

class mcisogem_histo_clot_police(osv.osv):
	_name = "mcisogem.histo.clot.police"
	_description="Historique de cloture de police"

	_columns = {
		'police_id' : fields.many2one('mcisogem.police' , 'Polices' , required=True),
		'exercice_ids' : fields.many2many('mcisogem.exercice.police' ,'mcisogem_histo_clot_rel','num_interne_police','id', 'Exercices', required=False),
		'dt_action' : fields.date('Date de Clôture'),
	}

	_rec_name="police_id"
	


	_defaults = {
		'dt_action' : time.strftime('%Y-%m-%d', time.localtime())
	}

	def create(self, cr, uid, data , context=None):
		exercices = data['exercice_ids']

		for exe_id in exercices[0][2]:
			#ex = self.pool.get('mcisogem.exercice.police').search(cr,uid,[('id', '=', exe)])
			self.pool.get('mcisogem.exercice.police').write(cr,uid,exe_id,{'bl_exercice_clot' : True},context=context)
		return super(mcisogem_histo_clot_police , self).create(cr,uid,data,context)
