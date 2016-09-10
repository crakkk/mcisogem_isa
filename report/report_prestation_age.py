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

class report_prestation_age(osv.osv):
	_name = "report.prestation.age"
	_description = "Graphes sur les prestation par tranche d'age"
	_auto = False
   

	_columns = {
		
		'garant_id': fields.many2one('mcisogem.garant', 'Garant', readonly=True),
		'police_id': fields.many2one('mcisogem.police', 'Police', readonly=True),
		'exercice_id': fields.many2one('mcisogem.exercice', 'Exercice', readonly=True),
		'periode_id': fields.many2one('mcisogem.account.period', 'Periode', readonly=True),
		'taux_moin_18': fields.float('Taux des -19 ans (%)', readonly=True),
		'mont_remb_moin_18': fields.integer('Montant remboursé (des -19 ans)', readonly=True),
		'taux_18_30': fields.float('Taux de 19 à 30 ans (%)', readonly=True),
		'mont_remb_18_30': fields.integer('Montant remboursé (de 19 à 30 ans)', readonly=True),
		'taux_30_60': fields.float('Taux de 31 à 60 ans (%)', readonly=True),
		'mont_remb_30_60': fields.integer('Montant remboursé (de 30 à 60 ans)', readonly=True),
		'taux_plus_60': fields.float('Taux des + 60 ans', readonly=True),
		'mont_remb_plus_60': fields.integer('Montant remboursé (des + 60 ans)', readonly=True),
		
		
	}
	
	_depends = {'mcisogem.garant': ['id','name'] ,'mcisogem.police' : ['id','name'] , 'mcisogem.exercice' : ['id','name','date_debut','date_fin'],'mcisogem.account.period' : ['id','name'] }


	def init_server(self, cr, uid, context):
		print('*************execute action serveur************')
		print('*************prestation age************')
		cr.execute("select report_prestation_age()")
		tools.drop_view_if_exists(cr, 'report_prestation_age')
		cr.execute("""
			create or replace view report_prestation_age as (
				 SELECT 

				 	min(mcisogem_report_stat_prestation_age.id) AS id, 
					mcisogem_report_stat_prestation_age.garant_id as garant_id,
					mcisogem_report_stat_prestation_age.police_id as police_id,
					mcisogem_report_stat_prestation_age.exercice_id as exercice_id,
					mcisogem_report_stat_prestation_age.periode_id as periode_id,
					SUM(mcisogem_report_stat_prestation_age.taux_moin_18) as taux_moin_18,
					SUM(mcisogem_report_stat_prestation_age.mont_remb_moin_18) as mont_remb_moin_18,
					SUM(mcisogem_report_stat_prestation_age.taux_18_30) as taux_18_30,
					SUM(mcisogem_report_stat_prestation_age.mont_remb_18_30) as mont_remb_18_30,
					SUM(mcisogem_report_stat_prestation_age.taux_30_60) as taux_30_60,
					SUM(mcisogem_report_stat_prestation_age.mont_remb_30_60) as mont_remb_30_60,
					SUM(mcisogem_report_stat_prestation_age.taux_plus_60) as taux_plus_60,
					SUM(mcisogem_report_stat_prestation_age.mont_remb_plus_60) as mont_remb_plus_60
					


    			FROM mcisogem_report_stat_prestation_age

    			group by
					garant_id, police_id, exercice_id, periode_id, taux_moin_18, mont_remb_moin_18, taux_18_30, mont_remb_18_30, taux_30_60, mont_remb_30_60, taux_plus_60, mont_remb_plus_60
				
			 
			)""")
		res = {}
		view_ids = self.pool.get('ir.ui.view').search(cr, uid, [('name' , '=' , 'report.prestation.age.graph')], context=context)
		if view_ids:
			res = {
			'view_id': view_ids[0],
			'view_mode': 'graph',
			'view_type': 'form',
			'res_model': 'report.prestation.age',
			'type': 'ir.actions.act_window',
			'context': context
			}
			print(res)
		else:
			print("TEST")
		return res



	def init(self, cr):
		tools.drop_view_if_exists(cr, 'report_prestation_age')
		cr.execute("""
			create or replace view report_prestation_age as (
				 SELECT 

				 	min(mcisogem_report_stat_prestation_age.id) AS id, 
					mcisogem_report_stat_prestation_age.garant_id as garant_id,
					mcisogem_report_stat_prestation_age.police_id as police_id,
					mcisogem_report_stat_prestation_age.exercice_id as exercice_id,
					mcisogem_report_stat_prestation_age.periode_id as periode_id,
					mcisogem_report_stat_prestation_age.taux_moin_18 as taux_moin_18,
					mcisogem_report_stat_prestation_age.mont_remb_moin_18 as mont_remb_moin_18,
					mcisogem_report_stat_prestation_age.taux_18_30 as taux_18_30,
					mcisogem_report_stat_prestation_age.mont_remb_18_30 as mont_remb_18_30,
					mcisogem_report_stat_prestation_age.taux_30_60 as taux_30_60,
					mcisogem_report_stat_prestation_age.mont_remb_30_60 as mont_remb_30_60,
					mcisogem_report_stat_prestation_age.taux_plus_60 as taux_plus_60,
					mcisogem_report_stat_prestation_age.mont_remb_plus_60 as mont_remb_plus_60
					


    			FROM mcisogem_report_stat_prestation_age

    			group by
					garant_id, police_id, exercice_id, periode_id, taux_moin_18, mont_remb_moin_18, taux_18_30, mont_remb_18_30, taux_30_60, mont_remb_30_60, taux_plus_60, mont_remb_plus_60
				
			)""")
	  


