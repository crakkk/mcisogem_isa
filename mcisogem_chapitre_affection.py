# -*- coding:utf8 -*-
import time

from openerp import SUPERUSER_ID
from openerp.osv import fields
from openerp.osv import osv
from datetime import datetime, timedelta
from openerp import tools
from openerp.tools.translate import _
import openerp
from datetime import datetime, timedelta, date
from dateutil import relativedelta
from dateutil.relativedelta import relativedelta
from dateutil import parser
import logging
_logger = logging.getLogger(__name__)


class mcisogem_chapitre_affection(osv.osv):
	_name = "mcisogem.chapitre.affection"
	_description = 'Chapitre des affections'

	_columns = {        
		'lbc_ref_chap' : fields.char('Référence chapitre' , required=True),
		'plage_ref_chap' : fields.char('Plage' , required=True) ,
		'lb_chap' : fields.char('Libellé' , required=True)
	}

	_rec_name = "lb_chap"

	def create(self, cr, uid, data, context=None):
		data['lbc_ref_chap'] = (data['lbc_ref_chap']).upper()
		data['lb_chap'] = (data['lb_chap']).upper()
		return super(mcisogem_chapitre_affection, self).create(cr, uid, data, context=context)



class mcisogem_sous_chapitre_affection(osv.osv):
	_name = "mcisogem.sous.chapitre.affection"
	_description = 'Sous Chapitre des affections'

	_columns = {        
		'chapitre_id' : fields.many2one('mcisogem.chapitre.affection'  , 'Chapitre' , required=True) , 
		'code_schap' : fields.char('Code' , required=True),
		'lb_schap' : fields.char('Libellé' , required=True)
	}
	_rec_name ="lb_schap"

	def create(self, cr, uid, data, context=None):
		data['code_schap'] = (data['code_schap']).upper()
		data['lb_schap'] = (data['lb_schap']).upper()
		return super(mcisogem_sous_chapitre_affection, self).create(cr, uid, data, context=context)