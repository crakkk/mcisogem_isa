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

class report_benef_report(osv.osv):
	_name = "report.benef.report"
	_description = "Graphes sur les Bénéficiaires"
	_auto = False
   

	_columns = {
		
		'garant_id': fields.many2one('mcisogem.garant', 'Garant', readonly=True),
		# 'souscripteur_id': fields.many2one('mcisogem.souscripteur', 'Souscripteur', readonly=True),
		'police_id': fields.many2one('mcisogem.police', 'Police', readonly=True),
		'exercice_id': fields.many2one('mcisogem.exercice', 'Exercice', readonly=True),
		'nbr_benef_crees': fields.integer('Crées', readonly=True),
		'nbr_benef_inc': fields.integer('Incorporés', readonly=True),
		'nbr_benef_ret': fields.integer('Rétirés', readonly=True),
		'nbr_benef_suspend': fields.integer('Suspendus', readonly=True),
		'nbr_benef_total': fields.integer('Total actif', readonly=True),
		'nbr_total': fields.integer('Total', readonly=True),
		
	}
	
	# _depends = {'mcisogem.garant': ['id','name'] ,'mcisogem.souscripteur' : ['id','name'] , 'mcisogem.police' : ['id','name'] , 'mcisogem.exercice' : ['id','name','date_debut','date_fin'] }
	_depends = {'mcisogem.garant': ['id','name'] , 'mcisogem.police' : ['id','name'] , 'mcisogem.exercice' : ['id','name','date_debut','date_fin'] }


	def init_server(self, cr, uid, context):
		print('*************execute action serveur************')
		print('*************benef report************')
		cr.execute("select report_benef()")
		tools.drop_view_if_exists(cr, 'report_benef_report')
		cr.execute("""
			create or replace view report_benef_report as (
				SELECT 

				 	
				 	min(mcisogem_report_stat_benef.id) AS id,  
				 	mcisogem_report_stat_benef.garant_id as garant_id,  
					mcisogem_report_stat_benef.exercice_id as exercice_id,
					mcisogem_report_stat_benef.police_id as police_id,
					mcisogem_report_stat_benef.nbr_benef_total as nbr_benef_total,
					mcisogem_report_stat_benef.nbr_total as nbr_total,
					mcisogem_report_stat_benef.nbr_benef_crees as nbr_benef_crees,
					mcisogem_report_stat_benef.nbr_benef_inc as nbr_benef_inc,
					mcisogem_report_stat_benef.nbr_benef_ret as nbr_benef_ret,
					mcisogem_report_stat_benef.nbr_benef_suspend as nbr_benef_suspend


    			FROM mcisogem_report_stat_benef

    			group by
					garant_id, exercice_id, police_id, nbr_benef_total,nbr_total,nbr_benef_crees, nbr_benef_inc,  nbr_benef_ret, nbr_benef_suspend
			)""")
		res = {}
		view_ids = self.pool.get('ir.ui.view').search(cr, uid, [('name' , '=' , 'report.benef.report.graph')], context=context)
		if view_ids:
			# if garant_id:
			res = {
			# 'res_id': garant_id,
			'view_id': view_ids[0],
			'view_mode': 'graph',
			'view_type': 'form',
			'res_model': 'report.benef.report',
			'type': 'ir.actions.act_window',
			'context': context
			}
			print(res)
		else:
			print("TEST")
		return res


	def init(self, cr):
		cr.execute("select report_benef()")
		tools.drop_view_if_exists(cr, 'report_benef_report')
		cr.execute("""
			create or replace view report_benef_report as (
				SELECT 

				 	
				 	min(mcisogem_report_stat_benef.id) AS id,  
				 	mcisogem_report_stat_benef.garant_id as garant_id,  
					mcisogem_report_stat_benef.exercice_id as exercice_id,
					mcisogem_report_stat_benef.police_id as police_id,
					mcisogem_report_stat_benef.nbr_benef_total as nbr_benef_total,
					mcisogem_report_stat_benef.nbr_benef_inc as nbr_benef_inc,
					mcisogem_report_stat_benef.nbr_benef_ret as nbr_benef_ret,
					mcisogem_report_stat_benef.nbr_benef_suspend as nbr_benef_suspend


    			FROM mcisogem_report_stat_benef

    			group by
					garant_id, exercice_id, police_id, nbr_benef_total, nbr_benef_inc,  nbr_benef_ret, nbr_benef_suspend
			)""")
	  


