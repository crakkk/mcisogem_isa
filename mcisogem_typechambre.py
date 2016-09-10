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

class mcisogem_typechambre(osv.osv):
	_name  = "mcisogem.type.chambre"
	_description = "Type de chambre"

	_columns= {

		'code_type_chambre' : fields.integer('Code'),
		'name' : fields.char('Libellé', size=30, required=True),
		'cod_sup' : fields.char('cod_sup', size=1),
	}
	
	def create(self, cr, uid, vals, context=None):
		#Récuperation du nombre de type de chambre puis définition du code de la chambre
		cr.execute("select * from mcisogem_type_chambre where id>%s", (0,))
		nb = len(cr.dictfetchall())
		vals['code_type_chambre'] = nb + 1
		return super(mcisogem_typechambre, self).create(cr, uid, vals, context=context)
