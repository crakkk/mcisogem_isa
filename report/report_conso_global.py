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

class report_conso_global(osv.osv):
	_name = "report.conso.global"
	_description = "consomation global"
	_auto = False
   

	_columns = {
		
		'exercice_id': fields.many2one('mcisogem.exercice', 'Exercice', readonly=True),
		'periode_id': fields.many2one('mcisogem.account.period', 'Periode', readonly=True),
		'montant_remb_total': fields.float('Montant remboursé total', readonly=True),
	}
	
	_depends = {'mcisogem.account.period' : ['id','name'] , 'mcisogem.exercice' : ['id','name','date_debut','date_fin']}



	def init_server(self, cr, uid, context):
		print('*************execute init************')
		print('*************consomation global************')
		cr.execute("select report_conso_max()")
		tools.drop_view_if_exists(cr, 'report_conso_global')
		cr.execute("""
			create or replace view report_conso_global as (
				 SELECT 

				 	min(mcisogem_report_stat_conso_global.id) AS id, 
					mcisogem_report_stat_conso_global.exercice_id as exercice_id,
					mcisogem_report_stat_conso_global.periode_id as periode_id,
					mcisogem_report_stat_conso_global.montant_remb_total as montant_remb_total
					


    			FROM mcisogem_report_stat_conso_global

    			group by
					exercice_id,periode_id, montant_remb_total
				
			 
			)""")
		res = {}
		view_ids = self.pool.get('ir.ui.view').search(cr, uid, [('name' , '=' , 'report.conso.global.line.graph')], context=context)
		if view_ids:
			# if garant_id:
			res = {
			# 'res_id': garant_id,
			'view_id': view_ids[0],
			'view_mode': 'graph',
			'view_type': 'form',
			'res_model': 'report.conso.global',
			'type': 'ir.actions.act_window',
			'context': context
			}
			print(res)
		else:
			print("TEST")
		return res

	def init(self, cr):
		print('*************execute init************')
		print('*************consomation global************')
		cr.execute("select report_conso_max()")
		tools.drop_view_if_exists(cr, 'report_conso_global')
		cr.execute("""
			create or replace view report_conso_global as (
				 SELECT 

				 	min(mcisogem_report_stat_conso_global.id) AS id, 
					mcisogem_report_stat_conso_global.exercice_id as exercice_id,
					mcisogem_report_stat_conso_global.periode_id as periode_id,
					mcisogem_report_stat_conso_global.montant_remb_total as montant_remb_total
					


    			FROM mcisogem_report_stat_conso_global

    			group by
					exercice_id,periode_id, montant_remb_total
				
			 
			)""")
	  


