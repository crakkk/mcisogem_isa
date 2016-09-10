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

class mcisogem_report_stat_prestation_age(osv.osv):
	_name = "mcisogem.report.stat.prestation.age"
	_description = "Graphes sur les prestation par tranche d'age stat"
	# _auto = False
   

	_columns = {
		
		'garant_id': fields.many2one('mcisogem.garant', 'Garant', readonly=True),
		'police_id': fields.many2one('mcisogem.police', 'Police', readonly=True),
		'exercice_id': fields.many2one('mcisogem.exercice', 'Exercice', readonly=True),
		'periode_id': fields.many2one('mcisogem.account.period', 'Periode', readonly=True),
		'taux_moin_18': fields.float('Taux -19', readonly=True),
		'mont_remb_moin_18': fields.integer('Montant remboursé -18', readonly=True),
		'taux_18_30': fields.float('Taux 19 à 30', readonly=True),
		'mont_remb_18_30': fields.integer('Montant remboursé 18 à 30', readonly=True),
		'taux_30_60': fields.float('Taux 31 à 60', readonly=True),
		'mont_remb_30_60': fields.integer('Montant remboursé 30 à 60', readonly=True),
		'taux_plus_60': fields.float('Taux + 60', readonly=True),
		'mont_remb_plus_60': fields.integer('Montant remboursé + 60', readonly=True),
		'mont_remb_total': fields.integer('Montant total', readonly=True),
		'prestation_id': fields.integer('prestation id', readonly=True),
		
	}
	
	# def init(self, cr):
	# 	print('*************execute init************')
	# 	print('*************les prescriptions************')
	# 	cr.execute("select report_prescription_med()")