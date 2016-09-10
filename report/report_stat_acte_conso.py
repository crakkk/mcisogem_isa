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

from openerp import tools
from openerp.osv import fields, osv

class mcisogem_report_stat_acte_conso(osv.osv):
	_name = "mcisogem.report.stat.acte.conso"
	_description = "Liste des actes + conso par periode"
	# _auto = False
   

	_columns = {
		
		'acte_id' :  fields.many2one('mcisogem.nomen.prest', 'Acte', readonly=True),
		'exercice_id': fields.many2one('mcisogem.exercice', 'Exercice', readonly=True),
		'periode_id': fields.many2one('mcisogem.account.period', 'Periode', readonly=True),
		'montant_total': fields.integer('Montant total remboursé', readonly=True),
		'nbr_taux_periode': fields.float('Taux (%)', readonly=True),
		
	}
	
	def init(self, cr):
		print('*************execute init************')
		print('*************les actes max************')
		cr.execute("select report_acte_conso_max()")


	def acte_conso_crone(self,cr,uid,context=None):
		print('*************execute init************')
		print('*************les actes max************')
		cr.execute("select report_acte_conso_max()")