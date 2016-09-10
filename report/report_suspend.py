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

class report_suspend(osv.osv):
	_name = "report.suspend"
	_description = "Graphes sur demande de suspension"
	_auto = False
   

	_columns = {
		
		
		'garant_id': fields.many2one('mcisogem.garant', 'Garant', readonly=True),
		'police_id': fields.many2one('mcisogem.police', 'Police', readonly=True),
		'exercice_id': fields.many2one('mcisogem.exercice', 'Exercice', readonly=True),
		'periode_id': fields.many2one('mcisogem.account.period', 'Periode', readonly=True),
		'nbr_attente': fields.integer('En attente', readonly=True),
		'nbr_valide': fields.integer('Valide', readonly=True),
		'nbr_rejete': fields.integer('Rejete', readonly=True),
		'nbr_total': fields.integer('Total', readonly=True),
		
	}
	
	_depends = {'mcisogem.garant': ['id','name'] , 'mcisogem.police' : ['id','name'] ,'mcisogem.account.period' : ['id','name'] , 'mcisogem.exercice' : ['id','name','date_debut','date_fin'], 'mcisogem.benef' : ['id','name']}



	def init_server(self, cr, uid, context):

		print('*************execute action serveur************')
		print('*************suspend report************')

		cr.execute("select report_suspend()")
		tools.drop_view_if_exists(cr, 'report_suspend')
		cr.execute("""
			create or replace view report_suspend as (
				 SELECT 

				 	min(mcisogem_report_stat_suspend.id) AS id,
					mcisogem_report_stat_suspend.garant_id as garant_id,  
					mcisogem_report_stat_suspend.exercice_id as exercice_id,
					mcisogem_report_stat_suspend.police_id as police_id,
					mcisogem_report_stat_suspend.periode_id as periode_id,
					mcisogem_report_stat_suspend.nbr_attente as nbr_attente,
					mcisogem_report_stat_suspend.nbr_valide as nbr_valide,
					mcisogem_report_stat_suspend.nbr_rejete as nbr_rejete,
					mcisogem_report_stat_suspend.nbr_total as nbr_total


    			FROM mcisogem_report_stat_suspend

    			group by
					garant_id,  exercice_id, police_id,periode_id, nbr_total, nbr_valide,  nbr_attente, nbr_rejete
 
			 
			)""")

		res = {}
		view_ids = self.pool.get('ir.ui.view').search(cr, uid, [('name' , '=' , 'report.suspend.graph')], context=context)
		if view_ids:
			# if garant_id:
			res = {
			# 'res_id': garant_id,
			'view_id': view_ids[0],
			'view_mode': 'graph',
			'view_type': 'form',
			'res_model': 'report.suspend',
			'type': 'ir.actions.act_window',
			'context': context
			}
			print(res)
		else:
			print("TEST")
		return res



	def init(self, cr):
		cr.execute("select report_suspend()")
		tools.drop_view_if_exists(cr, 'report_suspend')
		cr.execute("""
			create or replace view report_suspend as (
				 SELECT 

				 	min(mcisogem_report_stat_suspend.id) AS id,
					mcisogem_report_stat_suspend.garant_id as garant_id,  
					mcisogem_report_stat_suspend.exercice_id as exercice_id,
					mcisogem_report_stat_suspend.police_id as police_id,
					mcisogem_report_stat_suspend.periode_id as periode_id,
					mcisogem_report_stat_suspend.nbr_attente as nbr_attente,
					mcisogem_report_stat_suspend.nbr_valide as nbr_valide,
					mcisogem_report_stat_suspend.nbr_rejete as nbr_rejete,
					mcisogem_report_stat_suspend.nbr_total as nbr_total


    			FROM mcisogem_report_stat_suspend

    			group by
					garant_id,  exercice_id, police_id,periode_id, nbr_total, nbr_valide,  nbr_attente, nbr_rejete
 
			 
			)""")


	  


