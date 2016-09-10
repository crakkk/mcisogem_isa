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
# from common_report_header import common_report_header
from openerp import pooler


# class mcisogem_recherche_benef_garant(report_sxw.rml_parse , common_report_header):
class mcisogem_recherche_benef_garant(report_sxw.rml_parse):

	def __init__(self,cr,uid,name,context):
		super(mcisogem_recherche_benef_garant,self).__init__(cr,uid,name,context=context)
		self.localcontext.update({
		  'time': time,
		  'get_lines':self.get_lines,
		  'to_int' : self.AfficheEntier
	  })


	def get_lines(self,user,objects):
		lines =[]
		for obj in objects:
			if user.id == obj.user_id.id:
				lines.append(obj)
			return lines

	

	def _get_format(n): 
		# s = str(n)
		# l = len(s)
		# d = l / 3
		# for i in range(1,d+1):
		# 	s = s[:l-3*i] + sep + s[l-3*i:]
		return s

	
class report_benef_garant(osv.AbstractModel):
	_name = 'report.mcisogem_isa.benef_garant'
	# @api.multi
	def render_html(self, data=None):
		report_obj = self.env['report']
		report = report_obj._get_report_from_name('mcisogem_isa.report_benef_garant')
		docargs = {
		'doc_ids': self._ids,
		'doc_model': report.mcisogem.recherche.benef.garant,
		'docs': self,
		}
		return report_obj.render('mcisogem_isa.report_benef_garant', docargs)