# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
from openerp.osv import osv
from openerp.report import report_sxw
from openerp import pooler

	
class report_quittancier_mci(osv.AbstractModel):
	_name = 'report.mcisogem_isa.quittancier_mci'


	def render_html(self, data=None):
		report_obj = self.env['report']
		report = report_obj._get_report_from_name('mcisogem_isa.report_quittancier_mci')
		docargs = {
		'doc_ids': self._ids,
		'doc_model': report.mcisogem.quittancier,
		'docs': self
		}

		return report_obj.render('mcisogem_isa.report_quittancier_mci', docargs)
